# Smart Emergency Priority System (SEPS)

A **production-style simulation** of a national emergency dispatch platform (ambulance dispatch, live tracking, smart routing). This is **not** connected to real hospitals or government systems.

## Features

- **4 roles**: Citizen, Dispatcher/Admin, Ambulance Driver, Hospital Staff
- **Bilingual UI**: English + Arabic (RTL) via `next-intl`
- **Smart assignment**: Dijkstra & A* routing with traffic-aware ETA (`backend/app/services/route_optimizer.py`)
- **Live maps**: Leaflet with ambulances, emergencies, hospitals, traffic zones, routes
- **WebSockets**: Real-time positions, notifications, sound alerts
- **20+ Saudi hospitals** pre-seeded across major cities
- **Analytics**: Charts for response time, load, hotspots
- **Docker**: One-command startup with auto DB + seed

## Quick Start (Docker)

```bash
cp .env.example .env
docker-compose up --build
```

| Service   | URL                          |
|-----------|------------------------------|
| Frontend  | http://localhost:3000        |
| Backend   | http://localhost:8000        |
| API Docs  | http://localhost:8000/docs   |
| WebSocket | ws://localhost:8000/ws/all   |

## Demo Accounts

| Role       | Email               | Password    |
|------------|---------------------|-------------|
| Dispatcher | admin@system.com    | admin123    |
| Driver     | driver@system.com   | driver123   |
| Citizen    | citizen@system.com  | citizen123  |
| Hospital   | hospital@system.com | hospital123 |

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
pip install -r requirements.txt
# Start PostgreSQL and set DATABASE_URL in .env
uvicorn app.main:app --reload --port 8000
```

Database tables and demo data are created automatically on first startup.

**Reset database:**

```bash
cd backend
python scripts/reset_db.py
```

### Frontend

```bash
cd frontend
npm install
# Create .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
# NEXT_PUBLIC_WS_URL=ws://localhost:8000
npm run dev
```

Open http://localhost:3000/en

## Project Structure

See [docs/STRUCTURE.md](docs/STRUCTURE.md)

## API Overview

| Prefix            | Description              |
|-------------------|--------------------------|
| `/api/auth`       | Login, register, profile   |
| `/api/emergencies`| CRUD, assign, status     |
| `/api/ambulances` | Fleet + nearby search    |
| `/api/hospitals`  | Saudi hospital database  |
| `/api/routes`     | A*/Dijkstra route compute|
| `/api/analytics`  | Dashboard metrics        |
| `/api/traffic`    | Simulated traffic zones  |
| `/api/notifications` | User notifications    |
| `/ws/{channel}`   | WebSocket (all, dispatcher, driver) |

## Deployment

### Frontend → Vercel

1. Import `frontend/` as the project root.
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL` = your Render backend URL
   - `NEXT_PUBLIC_WS_URL` = `wss://your-backend.onrender.com`
3. Deploy.

### Backend → Render

1. Create a **PostgreSQL** instance on Render.
2. Create a **Web Service** from `backend/`:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS` (include your Vercel URL).
4. On deploy, tables and seed data run via `lifespan` hook.

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed steps.

## Simulation Notice

All emergencies, hospitals, and ambulances are **simulated**. Do not use this system for real medical emergencies.

## License

MIT — educational and demonstration use.
