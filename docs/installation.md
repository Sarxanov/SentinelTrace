# Installation

Use Python 3.11+, Node 22+, and SQLite for local development. Install backend requirements from `backend/requirements.txt`, run `alembic upgrade head`, then run `uvicorn app.main:app --reload` from `backend`. Run `npm install && npm run dev` from `frontend`. Docker Compose runs migrations before the backend and provides persistent SQLite storage.
