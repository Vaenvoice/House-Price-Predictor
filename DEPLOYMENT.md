# Vercel Deployment (Single Project)

This project is now configured for a single Vercel deployment:

- Frontend is built from `frontend/`
- FastAPI backend runs as a Vercel Python Function at `/api/index.py`

## 1) Push this project to GitHub

Commit and push the latest code to your repository.

## 2) Import project into Vercel

1. Open Vercel dashboard.
2. Click **Add New Project**.
3. Import your GitHub repo.
4. Keep project root as repository root (do not set to `frontend`).

Vercel uses `vercel.json` in root:

- Build command: `cd frontend && npm install && npm run build`
- Output directory: `frontend/dist`
- API function: `api/index.py`

## 3) Set required environment variables

In Vercel project settings -> **Environment Variables** add:

- `SECRET_KEY` = a long random secret value
- `FORCE_RETRAIN` = `false`

## 4) Deploy

Click **Deploy** (or push to main if auto-deploy is enabled).

After deployment:

- App URL: `https://<your-project>.vercel.app`
- API health: `https://<your-project>.vercel.app/`
- API docs: `https://<your-project>.vercel.app/docs`

## 5) Notes for Vercel runtime

- Serverless filesystem is ephemeral; runtime data is copied into `/tmp`.
- Bundled pretrained model artifacts are included from `backend/data/models`.
- Prediction APIs work without heavy cold-start retraining.
- Auth users/history are stored in SQLite in `/tmp`, so data is not guaranteed across cold starts.

For persistent users/history, move DB to a managed service (Vercel Postgres/Neon/Supabase).
