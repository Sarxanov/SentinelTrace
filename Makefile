backend-test:
	cd backend && alembic upgrade head && pytest -q --cov=app
backend-lint:
	cd backend && ruff check app tests
backend-migrate:
	cd backend && alembic upgrade head
frontend-install:
	cd frontend && npm install
frontend-build:
	cd frontend && npm run build
frontend-test:
	cd frontend && npm test
dev:
	cd backend && uvicorn app.main:app --reload
