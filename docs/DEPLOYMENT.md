# Deployment Guide (Vercel + Render)

## Prerequisites

- GitHub repository with this project
- [Vercel](https://vercel.com) account
- [Render](https://render.com) account

## 1. Deploy Backend on Render

### PostgreSQL

1. Create **PostgreSQL** on Render.
2. Copy the **Internal Database URL**.

### Web Service

1. New **Web Service** → connect repo.
2. Root directory: `backend`
3. Runtime: Python 3
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables

```
DATABASE_URL=<render-postgres-url>
SECRET_KEY=<long-random-string>
CORS_ORIGINS=https://your-app.vercel.app
SIMULATION_TICK_SECONDS=2
```

### Health Check

Path: `/health`

After deploy, open `https://your-service.onrender.com/docs` to verify APIs.

## 2. Deploy Frontend on Vercel

1. Import project; set **Root Directory** to `frontend`.
2. Framework: Next.js (auto-detected).
3. Environment variables:

```
NEXT_PUBLIC_API_URL=https://your-service.onrender.com
NEXT_PUBLIC_WS_URL=wss://your-service.onrender.com
```

4. Deploy.

## 3. WebSockets on Render

Render supports WebSockets on web services. Use `wss://` in production.

## 4. Post-Deploy Checklist

- [ ] Login with demo accounts
- [ ] Create test emergency as citizen
- [ ] Verify dispatcher map updates
- [ ] Accept as driver and watch live movement
- [ ] Switch language EN/AR

## 5. Docker Production (optional)

Use `docker-compose.yml` on any VPS with Docker installed:

```bash
docker-compose up -d --build
```

Update `CORS_ORIGINS` and public URLs in `.env`.
