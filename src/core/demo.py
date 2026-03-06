import os

from src.core.rag_system import RAGSystem
from src.utils.utils import create_sample_docs_folder, load_env_vars


def run_demo():
    """运行简单演示流程。"""
    print("正在运行RAG系统演示...")

    try:
        load_env_vars()
    except ValueError as e:
        print(f"错误: {e}")
        return

    try:
        rag_system = RAGSystem()
    except ValueError as e:
        print(f"错误: {e}")
        return

    create_sample_docs_folder()
    print("已创建示例文档")

    sample_path = os.path.join(os.getcwd(), "sample_docs")
    print(f"正在处理示例文档: {sample_path}")
    rag_system.process_and_store(sample_path)

    questions = [
        "AI Solutions公司是做什么的？",
        "AI Solutions公司是什么时候成立的？",
        "AI Solutions公司提供哪些服务？",
    ]

    print("\n开始演示问答:")
    for question in questions:
        print(f"\n问题: {question}")
        result = rag_system.query(question)
        print(f"答案: {result['answer']}")

        if result["source_documents"]:
            print("参考资料片段:")
            for i, source in enumerate(result["source_documents"][:2], 1):
                print(f"  {i}. {source[:150]}...")
