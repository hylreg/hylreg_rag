# Operations Runbook

## Common Incidents

## 1. API returns 401

Possible causes:

- `API_AUTH_TOKEN` configured but request missing/invalid `Authorization` header.

Actions:

1. Verify client sends `Authorization: Bearer <token>`.
2. Confirm server `.env` token value.

## 2. API returns 429

Possible causes:

- Per-IP request rate exceeded `API_RATE_LIMIT_PER_MINUTE`.

Actions:

1. Check traffic source/IP.
2. Tune limit if needed.
3. Add queue/retry logic on client side.

## 3. API returns 500 on query

Possible causes:

- RAG system not initialized
- Missing/invalid OpenAI credentials
- Vector index unavailable

Actions:

1. Check service logs.
2. Check `OPENAI_API_KEY`.
3. Check `/api/v1/health`.
4. Trigger `/api/v1/reload-index/` if index exists.

## 4. Upload fails with 413

Possible causes:

- File exceeds `API_MAX_UPLOAD_SIZE_MB`.

Actions:

1. Reduce upload file size.
2. Increase configured limit carefully.

## Routine Checks

1. `GET /api/v1/health`
2. `GET /api/v1/metrics`
3. Review request latency and error rate trends
4. Confirm backups of vectorstore are recent

## Emergency Rollback

1. Roll back to previous release tag
2. Restore previous vectorstore backup if schema/compat changed
3. Restart service and re-check health
