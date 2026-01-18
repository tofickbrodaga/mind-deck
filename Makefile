.PHONY: help build up down restart logs migrate test clean dev start-frontend start-backend

help:
	@echo "Available commands:"
	@echo "  make up            - Start everything with Docker Compose (recommended!)"
	@echo "  make dev           - Start everything (backend + frontend + DB) - local"
	@echo "  make build         - Build Docker images"
	@echo "  make down          - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - Show logs"
	@echo "  make migrate       - Run database migrations"
	@echo "  make test          - Run tests"
	@echo "  make clean         - Clean up containers and volumes"
	@echo "  make start-backend - Start backend only (local)"
	@echo "  make start-frontend - Start frontend only (local)"

build:
	docker-compose build

up:
	@echo "🚀 Запуск всех сервисов через Docker Compose..."
	@echo "📦 Запускаются: PostgreSQL, Redis, Backend, Frontend"
	@docker-compose up -d
	@echo ""
	@echo "✅ Все сервисы запущены!"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "📱 Фронтенд:  http://localhost:3000"
	@echo "🔧 Бэкенд:    http://localhost:8000"
	@echo "📚 API Docs:  http://localhost:8000/docs"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@echo "Просмотр логов: make logs"
	@echo "Остановка: make down"

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f app

migrate:
	docker-compose exec app alembic upgrade head

test:
	docker-compose exec app pytest

clean:
	docker-compose down -v
	docker system prune -f

# Запуск всего проекта для разработки
dev:
	@echo "🚀 Запуск MindDeck..."
	@bash start.sh

# Запуск только бэкенда
start-backend:
	@echo "🔧 Запуск бэкенда..."
	@docker-compose up -d postgres redis
	@sleep 3
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		. venv/bin/activate && pip install -q -r requirements.txt; \
	fi
	@. venv/bin/activate && alembic upgrade head
	@. venv/bin/activate && uvicorn presentation.api.main:app --host 0.0.0.0 --port 8000 --reload

# Запуск только фронтенда
start-frontend:
	@echo "🎨 Запуск фронтенда..."
	@cd frontend && npm install && npm run dev
