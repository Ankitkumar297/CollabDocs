# CollabDocs

Google Docs inspired document editor built with React, TypeScript, Vite, Tailwind, Tiptap, FastAPI, SQLAlchemy, and PostgreSQL.

## Local setup

Requires Node.js 20+, Python 3.12+, and PostgreSQL 16 (or Docker). From the repository root, start PostgreSQL with `docker compose up -d db`. Create `backend/.env` from `backend/.env.example` and set `DATABASE_URL=postgresql+psycopg://collabdocs:localpassword@localhost:5432/collabdocs`. Environment variables are read by the process; load the `.env` file in your shell or with your host's environment settings. For local smoke testing only, omit `DATABASE_URL` to use SQLite.

Run the API:

```sh
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Run the frontend in another terminal:

```sh
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173. API docs are at http://localhost:8000/docs. Alice and Bob are seeded on first API startup. The user switcher sends an `X-User-Id` header for demonstration. **It is not production authentication** and must be replaced before use with real users.

Import UTF-8 `.txt` and `.md` files up to 1 MB. Markdown headings up to level 3 are converted; other Markdown syntax imports as editable text.

## Verification

`cd backend && python -m pytest -q` runs API tests. `cd frontend && npm run lint && npm run build` checks the frontend.

## Deployment

Provision a managed PostgreSQL database. Deploy `backend/` as a Docker service on Render or Railway, with `DATABASE_URL` and `CORS_ORIGINS` set to the production frontend origin. The service starts with the included Dockerfile and exposes `/health`. Deploy `frontend/` to Vercel with Vite framework preset, build command `npm run build`, output directory `dist`, and `VITE_API_URL` set to the HTTPS backend origin. Redeploy the frontend after setting that build-time variable. Ensure the backend CORS origin exactly matches the Vercel URL. Production deployment requires service credentials and a database URL.
