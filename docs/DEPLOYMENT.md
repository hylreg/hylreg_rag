# Deployment Guide

## Prerequisites

- Python 3.12+
- Valid `OPENAI_API_KEY`
- Reverse proxy (recommended): Nginx or Caddy

## Environment

Create `.env` from template and set:

- `OPENAI_API_KEY`
- `RAG_VECTORSTORE_DIR`
- `API_AUTH_TOKEN` (recommended in production)
- `API_RATE_LIMIT_PER_MINUTE`

## Start Service

```bash
python run.py api --host 0.0.0.0 --port 8000
```

## Health and Metrics

- Health: `GET /api/v1/health`
- Metrics: `GET /api/v1/metrics`

## Reverse Proxy Notes

1. Forward `X-Forwarded-For` to preserve client IP for rate limiting.
2. Terminate TLS at proxy.
3. Limit request body size at proxy and app layers.

## Persistence and Backup

- Vector index directory: `RAG_VECTORSTORE_DIR` (default `data/vectorstore`)
- Backup strategy:
1. Periodic snapshot of vectorstore directory
2. Version backups by date
3. Verify restore by reloading index endpoint

## Upgrade Checklist

1. Pull latest code
2. Install dependencies (`pip install -e .`)
3. Run tests (`pytest -q`)
4. Restart service
5. Verify `/api/v1/health` and `/api/v1/metrics`
