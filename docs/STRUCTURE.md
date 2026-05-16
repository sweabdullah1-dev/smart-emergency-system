# Project Structure

```
smart-emergency-priority-system/
├── frontend/                 # Next.js 14 + React + TypeScript + Tailwind
│   ├── locales/              # en.json, ar.json (i18n)
│   ├── public/
│   └── src/
│       ├── app/[locale]/     # Localized routes
│       ├── components/       # UI, map, layout
│       ├── hooks/
│       └── lib/              # API, WebSocket, utils
├── backend/                  # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/routes/       # REST endpoints
│   │   ├── core/             # Config, security
│   │   ├── db/               # Session, seed
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Routing, dispatch, simulation
│   │   └── websocket/        # Real-time manager
│   ├── alembic/
│   └── scripts/reset_db.py
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── docs/
├── docker-compose.yml
├── .env.example
└── README.md
```
