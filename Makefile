.PHONY: dev web-build run

dev:
	(uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &) && cd web && npm run dev

web-build:
	cd web && npm install && npm run build

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000
