# Makefile
.PHONY: help install run-backend run-frontend run-all test clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install       - Install all dependencies"
	@echo "  make run-backend   - Run the FastAPI backend"
	@echo "  make run-frontend  - Run the Dash frontend"
	@echo "  make run-all       - Run both backend and frontend"
	@echo "  make docker-up     - Start services with Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean cache and temporary files"

install:
	pip install -r requirements.txt

run-backend:
	uvicorn main:app --reload --host 0.0.0.0 --port 8443

run-frontend:
	python dashboard.py

run-all:
	make run-backend & make run-frontend

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f

test:
	python -m pytest tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".DS_Store" -delete