# 架构说明

## 分层

1. `src/config`：基于环境变量的配置与校验。
2. `src/core`：RAG 编排（加载、分块、向量索引、查询）。
3. `src/utils`：通用工具与本地示例数据生成。
4. `src/cli`：命令行用户界面与入口。
5. `src/api`：围绕核心引擎的 FastAPI 服务封装。

## 运行流程

1. 从 `.env` 加载配置并处理环境变量。
2. 使用模型/分块/检索参数初始化 `RAGSystem`。
3. 加载并切分文档。
4. 构建或更新 FAISS 向量库。
5. 通过 LangChain `RetrievalQA` 执行检索与生成。

## 持久化

- 默认向量库路径：`data/vectorstore`。
- 自动持久化由 `RAG_AUTO_PERSIST` 控制。
- API/CLI 都提供显式保存与重新加载操作。

## 扩展点

- 在 `src/core/rag_system.py` 替换向量后端。
- 在 `src/config/settings.py` 与核心初始化中新增模型提供方支持。
- 在 `_load_single_document` 与 `_load_directory_documents` 中新增文档加载器。
