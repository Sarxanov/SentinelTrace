# Installation

Use Python 3.11+, Node 22+, and SQLite for local development. Install backend requirements from `backend/requirements.txt`, run `uvicorn app.main:app --reload` from `backend`, then run `npm install && npm run dev` from `frontend`. Docker Compose provides the same two-service arrangement with persistent SQLite storage.
