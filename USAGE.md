# HylReg-RAG 使用说明

## 快速开始

### 使用uv安装依赖（推荐）

如果你使用uv作为包管理器：

```bash
# 安装项目依赖
uv pip install -r requirements.txt

# 或者直接安装pyproject.toml中的依赖
uv pip install -e .

# 如果要开发模式安装（包含开发依赖）
uv pip install -e ".[dev]"
```

### 使用pip安装依赖

```bash
pip install -r requirements.txt
```

或者直接安装pyproject.toml中的依赖：

```bash
pip install -e .
```

### 2. 配置API密钥

复制 `.env.example` 文件为 `.env` 并填入你的 OpenAI API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，替换 `your_openai_api_key_here` 为实际的API密钥。

可选参数：

- `RAG_VECTORSTORE_DIR`：本地向量索引目录（默认 `data/vectorstore`）
- `RAG_AUTO_PERSIST`：处理/添加文档后自动保存索引（默认 `true`）
- `RAG_CHUNK_SIZE`、`RAG_CHUNK_OVERLAP`、`RAG_RETRIEVAL_K`
- `API_MAX_UPLOAD_SIZE_MB`、`API_ALLOWED_EXTENSIONS`

## 运行项目

项目提供了统一的运行脚本 `run.py`：

```bash
# 运行演示（默认）
python run.py

# 运行演示
python run.py demo

# 运行命令行界面
python run.py cli

# 运行API服务器
python run.py api
```

## 命令行使用（传统方式）

### 交互模式

```bash
python -m src.cli.cli_interface --interactive --file path/to/your/document.pdf
```

### 单次查询

```bash
python -m src.cli.cli_interface --file path/to/your/document.pdf --question "你的问题"
```

### 创建示例文档

```bash
python -m src.cli.cli_interface --create-sample
```

### 索引加载/保存

```bash
python -m src.cli.cli_interface --load-index
python -m src.cli.cli_interface --file sample_docs --save-index
```

## API服务器使用

启动API服务器：

```bash
python run.py api
# 或者使用uvicorn
uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000
```

### API端点

- `GET /` - 检查服务器状态
- `POST /process-document/` - 上传并处理文档
- `POST /query/` - 查询已处理的文档
- `POST /add-document/` - 向现有知识库添加文档
- `GET /health` - 健康检查
- `POST /save-index/` - 手动保存向量索引
- `POST /reload-index/` - 重新加载向量索引

#### 示例API调用

上传文档：
```bash
curl -X POST -F "file=@path/to/your/document.pdf" http://localhost:8000/process-document/
```

查询文档：
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"question":"你的问题"}' \
     http://localhost:8000/query/
```

## 支持的文档格式

- PDF (.pdf)
- 文本文件 (.txt)
- Word文档 (.docx)
- 目录（包含上述任何格式的文件）

## 架构说明

- `src/core/rag_system.py`: RAG系统的核心实现
- `src/config/settings.py`: 统一配置入口
- `src/cli/cli_interface.py`: 命令行接口
- `src/api/api_server.py`: REST API服务
- `src/utils/utils.py`: 实用工具函数
- `run.py`: 统一入口点
- `main.py`: 主程序入口（保留向后兼容性）
