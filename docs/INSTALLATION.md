# Installation Guide

## Option A: Docker (Recommended for beginners)

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
2. Clone or download this project
3. Copy environment file:

```bash
cp .env.example .env
```

4. Start everything:

```bash
docker-compose up --build
```

5. Wait until you see backend logs: `Database seeded successfully`
6. Open http://localhost:3000/en

## Option B: Manual setup

### PostgreSQL

```bash
# Using Docker for DB only:
docker run -d --name seps-db -e POSTGRES_USER=seps_user -e POSTGRES_PASSWORD=seps_password -e POSTGRES_DB=smart_emergency -p 5432:5432 postgres:16-alpine
```

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://seps_user:seps_password@localhost:5432/smart_emergency
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_WS_URL=ws://localhost:8000" >> .env.local
npm run dev
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| DB connection refused | Wait for Postgres healthcheck; check `DATABASE_URL` |
| Map not loading | Ensure client-side only; refresh page |
| 401 on API | Login again; token stored in `localStorage` |
| CORS error | Add frontend URL to `CORS_ORIGINS` in backend `.env` |

## Reset demo data

```bash
cd backend && python scripts/reset_db.py
```
