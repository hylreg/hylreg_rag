# 部署指南

## 前置条件

- Python 3.12+
- 有效的 `OPENAI_API_KEY`
- 反向代理（推荐）：Nginx 或 Caddy

## 环境配置

从模板创建 `.env` 并设置：

- `OPENAI_API_KEY`
- `RAG_VECTORSTORE_DIR`
- `API_AUTH_TOKEN`（生产环境推荐）
- `API_RATE_LIMIT_PER_MINUTE`

## 启动服务

```bash
python run.py api --host 0.0.0.0 --port 8000
```

## 健康检查与指标

- 健康检查：`GET /api/v1/health`
- 指标：`GET /api/v1/metrics`

## 反向代理说明

1. 转发 `X-Forwarded-For`，用于按客户端 IP 限流。
2. 在代理层终止 TLS。
3. 在代理层和应用层同时限制请求体大小。

## 持久化与备份

- 向量索引目录：`RAG_VECTORSTORE_DIR`（默认 `data/vectorstore`）
- 备份策略：
1. 周期性快照向量库目录
2. 按日期做版本化备份
3. 通过重载索引接口验证可恢复性

## 升级检查清单

1. 拉取最新代码
2. 安装依赖（`pip install -e .`）
3. 运行测试（`pytest -q`）
4. 重启服务
5. 验证 `/api/v1/health` 和 `/api/v1/metrics`
