# Makefile for AI Workflow 24H

.PHONY: help install dev test clean docker-up docker-down run

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development environment"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean cache and temp files"
	@echo "  make docker-up  - Start Docker services"
	@echo "  make docker-down - Stop Docker services"
	@echo "  make run        - Run the application"

install:
	python -m venv venv
	./venv/Scripts/activate && pip install -r requirements.txt

dev: docker-up
	./venv/Scripts/activate && uvicorn src.main:app --reload --port 8000

test:
	./venv/Scripts/activate && pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache

docker-up:
	docker-compose up -d
	@echo "Waiting for services to start..."
	@sleep 5
	docker-compose ps

docker-down:
	docker-compose down

run:
	./venv/Scripts/activate && python -m src.main

# Ollama 설치 및 모델 다운로드
ollama-setup:
	@echo "Installing Ollama models..."
	ollama pull llama2:7b
	ollama pull mistral

# 전체 초기 설정
setup: install docker-up ollama-setup
	@echo "Setup complete! Run 'make dev' to start development"