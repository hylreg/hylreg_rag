# 运维手册

## 常见故障

## 1. API 返回 401

可能原因：

- 已配置 `API_AUTH_TOKEN`，但请求缺少或携带了无效 `Authorization` 头。

处理步骤：

1. 确认客户端发送 `Authorization: Bearer <token>`。
2. 确认服务端 `.env` 中的 token 值。

## 2. API 返回 429

可能原因：

- 单 IP 请求速率超过 `API_RATE_LIMIT_PER_MINUTE`。

处理步骤：

1. 检查流量来源/IP。
2. 按需调整限流阈值。
3. 在客户端增加排队/重试逻辑。

## 3. 查询时 API 返回 500

可能原因：

- RAG 系统未初始化
- OpenAI 凭据缺失或无效
- 向量索引不可用

处理步骤：

1. 检查服务日志。
2. 检查 `OPENAI_API_KEY`。
3. 检查 `/api/v1/health`。
4. 若索引存在，触发 `/api/v1/reload-index/`。

## 4. 上传失败并返回 413

可能原因：

- 文件超过 `API_MAX_UPLOAD_SIZE_MB` 限制。

处理步骤：

1. 减小上传文件大小。
2. 谨慎增大配置上限。

## 日常巡检

1. `GET /api/v1/health`
2. `GET /api/v1/metrics`
3. 观察请求延迟与错误率趋势
4. 确认向量库备份是否及时

## 紧急回滚

1. 回滚到上一个发布标签
2. 若 schema/兼容性变化，恢复上一个向量库备份
3. 重启服务并重新检查健康状态
