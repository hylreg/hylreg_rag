import os
from typing import List, Optional
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import (
    DirectoryLoader,
    Docx2txtLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config.settings import Settings, get_settings

class RAGSystem:
    """
    检索增强生成(Retrieval-Augmented Generation)系统
    用于文档问答和信息检索
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        settings: Optional[Settings] = None,
    ):
        """
        初始化RAG系统
        
        Args:
            openai_api_key: OpenAI API密钥，如果未提供则尝试从环境变量获取
        """
        self.settings = settings or get_settings()

        if openai_api_key:
            os.environ["OPENAI_API_KEY"] = openai_api_key
            api_key = openai_api_key
        else:
            api_key = self.settings.openai_api_key

        if not api_key:
            raise ValueError("必须提供OpenAI API密钥")

        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            length_function=len,
        )
        os.environ["OPENAI_API_KEY"] = api_key
        if self.settings.openai_api_base:
            os.environ["OPENAI_API_BASE"] = self.settings.openai_api_base
        self.llm = OpenAI(temperature=self.settings.temperature)
        self.vectorstore = None
        self.qa_chain = None
        self.vectorstore_dir = self.settings.vectorstore_dir

        # 尝试自动加载已有向量索引
        self.load_vectorstore(silent=True)

    def _load_single_document(self, file_path: str) -> List:
        """按文件扩展名加载单个文档。"""
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".docx":
            loader = Docx2txtLoader(file_path)
        elif ext == ".txt":
            loader = TextLoader(file_path, encoding="utf-8")
        else:
            raise ValueError(f"不支持的文件类型: {ext}")

        return loader.load()

    def _load_directory_documents(self, directory_path: str) -> List:
        """加载目录中的受支持文件类型（PDF/TXT/DOCX）。"""
        loader_specs = [
            ("**/*.pdf", PyPDFLoader, {}),
            ("**/*.txt", TextLoader, {"encoding": "utf-8"}),
            ("**/*.docx", Docx2txtLoader, {}),
        ]
        documents = []
        for pattern, loader_cls, loader_kwargs in loader_specs:
            loader = DirectoryLoader(
                directory_path,
                glob=pattern,
                loader_cls=loader_cls,
                loader_kwargs=loader_kwargs,
                show_progress=True,
                use_multithreading=True,
                silent_errors=True,
            )
            documents.extend(loader.load())

        if not documents:
            raise ValueError("目录中未找到受支持的文档（.pdf/.txt/.docx）")
        return documents
    
    def load_documents(self, file_path: str) -> List:
        """
        加载文档，支持PDF、TXT、DOCX格式
        
        Args:
            file_path: 文件路径或目录路径
            
        Returns:
            加载的文档列表
        """
        if os.path.isdir(file_path):
            return self._load_directory_documents(file_path)
        return self._load_single_document(file_path)
    
    def process_and_store(self, file_path: str):
        """
        处理文档并将其存储在向量数据库中
        
        Args:
            file_path: 要处理的文件路径或目录路径
        """
        # 加载文档
        documents = self.load_documents(file_path)
        
        # 分割文档
        texts = self.text_splitter.split_documents(documents)
        
        # 创建向量数据库
        self.vectorstore = FAISS.from_documents(texts, self.embeddings)
        
        # 创建问答链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": self.settings.retrieval_k}
            ),
            return_source_documents=True
        )
        if self.settings.auto_persist:
            self.save_vectorstore()
    
    def query(self, question: str) -> dict:
        """
        对知识库进行查询
        
        Args:
            question: 查询问题
            
        Returns:
            包含答案和源文档的字典
        """
        if not self.qa_chain:
            raise ValueError("请先调用process_and_store方法处理文档")
        
        response = self.qa_chain({"query": question})
        
        return {
            "answer": response["result"],
            "source_documents": [doc.page_content for doc in response["source_documents"]]
        }
    
    def add_document(self, file_path: str):
        """
        向现有的向量数据库添加新文档
        
        Args:
            file_path: 要添加的文件路径
        """
        documents = self.load_documents(file_path)
        texts = self.text_splitter.split_documents(documents)
        
        if self.vectorstore:
            # 将新文档添加到现有向量数据库
            self.vectorstore.add_documents(texts)
        else:
            # 如果没有现有向量数据库，则创建新的
            self.vectorstore = FAISS.from_documents(texts, self.embeddings)
        
        # 更新问答链
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": self.settings.retrieval_k}
            ),
            return_source_documents=True
        )
        if self.settings.auto_persist:
            self.save_vectorstore()

    def save_vectorstore(self, path: Optional[str] = None):
        """
        将向量数据库持久化到本地。
        """
        if not self.vectorstore:
            raise ValueError("当前没有可保存的向量数据库")

        target_path = path or self.vectorstore_dir
        os.makedirs(target_path, exist_ok=True)
        self.vectorstore.save_local(target_path)

    def load_vectorstore(self, path: Optional[str] = None, silent: bool = False):
        """
        从本地加载向量数据库并恢复问答链。
        """
        target_path = path or self.vectorstore_dir
        if not os.path.isdir(target_path):
            return

        try:
            self.vectorstore = FAISS.load_local(
                target_path,
                self.embeddings,
                allow_dangerous_deserialization=True,
            )
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vectorstore.as_retriever(
                    search_kwargs={"k": self.settings.retrieval_k}
                ),
                return_source_documents=True,
            )
        except Exception:
            if not silent:
                raise
