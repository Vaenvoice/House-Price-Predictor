# House Price Predictor (VaenEstate)

Full-stack AI house price prediction platform with:

- React + Vite frontend
- FastAPI backend
- ML prediction pipeline (scikit-learn + XGBoost)
- Single-project Vercel deployment support

## Tech Stack

- **Frontend:** React, Vite, Tailwind CSS, Recharts, Framer Motion
- **Backend:** FastAPI, Pydantic, SQLite (runtime), JWT auth
- **ML:** scikit-learn, XGBoost, joblib
- **Deployment:** Vercel (frontend + serverless API), Docker (optional local)

## Project Structure

- `frontend/` - UI app
- `backend/` - FastAPI app + ML pipeline
- `api/index.py` - Vercel Python serverless entrypoint
- `vercel.json` - Vercel build + routing config
- `DEPLOYMENT.md` - deployment steps

## Run Locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:3000` (or next free port)
- Backend docs: `http://localhost:8000/docs`

## Deploy

Primary target is **Vercel (single project)**.

See `DEPLOYMENT.md` for exact steps.

## Environment Variables

Use repository root `.env.example` as reference:

- `SECRET_KEY`
- `FORCE_RETRAIN`

Never commit real secrets.
