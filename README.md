# HylReg-RAG: 检索增强生成系统
[![CI](https://github.com/hylreg/hylreg_rag/actions/workflows/ci.yml/badge.svg)](https://github.com/hylreg/hylreg_rag/actions/workflows/ci.yml)
[![Security](https://github.com/hylreg/hylreg_rag/actions/workflows/security.yml/badge.svg)](https://github.com/hylreg/hylreg_rag/actions/workflows/security.yml)

这是一个基于检索增强生成（Retrieval-Augmented Generation, RAG）技术的智能问答系统。该系统能够利用外部知识库来回答用户问题，适用于文档问答、知识库查询等场景。

## 功能特性

- 向量数据库存储和检索
- 文档分块和嵌入
- 基于大语言模型的问答生成
- 支持多种文档格式（PDF, DOCX, TXT等）
- 本地向量索引持久化（FAISS）
- API上传大小与类型安全校验
- 环境变量集中配置（RAG参数/API参数）
- API版本化路由（`/api/v1`）与 Prometheus 指标（`/api/v1/metrics`）
- 支持可选 Bearer Token 鉴权与按 IP 限流

## 项目结构

```
hylreg_rag/
├── src/                 # 源代码目录
│   ├── config/          # 配置中心
│   │   └── settings.py
│   ├── core/            # 核心RAG引擎
│   │   ├── demo.py
│   │   └── rag_system.py
│   ├── utils/           # 工具模块
│   │   └── utils.py
│   ├── cli/             # 命令行接口
│   │   └── cli_interface.py
│   └── api/             # API服务
│       └── api_server.py
├── tests/               # 自动化测试
├── Makefile             # 常用开发命令
├── sample_docs/         # 示例文档目录
├── main.py              # 主程序入口
├── requirements.txt     # 项目依赖
├── USAGE.md             # 使用说明
└── .env.example         # 环境变量示例
```

## 技术栈

- Python 3.12+
- LangChain框架
- FAISS向量数据库
- OpenAI API或其他LLM
- FastAPI（用于API服务）

## 开源维护

- 贡献指南: [CONTRIBUTING.md](CONTRIBUTING.md)
- 安全策略: [SECURITY.md](SECURITY.md)
- 行为准则: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- 变更记录: [CHANGELOG.md](CHANGELOG.md)
- 许可证: [LICENSE](LICENSE)
- 架构文档: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- 维护指南: [docs/MAINTENANCE.md](docs/MAINTENANCE.md)
- 部署指南: [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)
- 运维手册: [docs/RUNBOOK.md](docs/RUNBOOK.md)

## 安装

使用uv（推荐）：
```bash
uv pip install -r requirements.txt
# 或者
uv pip install -e .
```

使用pip：
```bash
pip install -r requirements.txt
```

安装后也可使用控制台命令：
```bash
hylreg-rag-demo
hylreg-rag-cli --help
hylreg-rag-api
```

## 使用方法

```bash
python run.py demo
```

更多使用详情，请参阅 [USAGE.md](USAGE.md)。
