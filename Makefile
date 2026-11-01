backend-test:
	cd backend && pytest -q --cov=app
backend-lint:
	cd backend && ruff check app tests
frontend-install:
	cd frontend && npm install
frontend-build:
	cd frontend && npm run build
dev:
	cd backend && uvicorn app.main:app --reload
