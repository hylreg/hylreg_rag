# 贡献指南

感谢你考虑为本项目做出贡献。

## 开发环境准备

1. 创建并激活虚拟环境。
2. 安装依赖：
```bash
uv pip install -e ".[dev]"
```
3. 安装 git hooks：
```bash
pre-commit install
```
4. 复制环境变量模板：
```bash
cp .env.example .env
```

## 本地检查

在提交 PR 前运行所有检查：

```bash
make test
black --check .
flake8 src tests
mypy src
```

## 分支与 PR

1. 从 `main` 创建功能分支。
2. 保持改动聚焦且尽量小。
3. 对行为变更补充或更新测试。
4. 必要时更新文档（`README.md`、`USAGE.md`、changelog）。
5. 使用模板创建 PR，并确保 CI 通过。

## 提交信息

使用简洁的祈使句式提交信息，例如：

- `feat(api): add upload size guard`
- `fix(core): handle empty vector index`
- `docs: clarify environment variables`

## 问题反馈

请使用 issue 模板并提供：

- 复现步骤
- 期望行为与实际行为
- 环境信息（操作系统、Python 版本、依赖版本）
