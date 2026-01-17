.PHONY: help build up down restart logs migrate test clean

help:
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make up         - Start all services"
	@echo "  make down       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - Show logs"
	@echo "  make migrate    - Run database migrations"
	@echo "  make test       - Run tests"
	@echo "  make clean      - Clean up containers and volumes"

build:
	docker-compose build

up:
	docker-compose up -d

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
