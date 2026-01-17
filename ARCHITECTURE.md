# Архитектура MindDeck

## Обзор

MindDeck построен на принципах **Clean Architecture** 

## Структура проекта

```
mind-deck/
├── domain/                  # Доменный слой (бизнес-логика)
│   ├── entities/            # Сущности домена
│   │   ├── user.py
│   │   ├── deck.py
│   │   ├── card.py
│   │   └── study_session.py
│   └── repositories/        # Интерфейсы репозиториев
│       ├── user_repository.py
│       ├── deck_repository.py
│       ├── card_repository.py
│       └── study_session_repository.py
│
├── application/             # Слой приложения (use cases)
│   ├── use_cases/           # Use cases (бизнес-сценарии)
│   │   ├── deck_use_cases.py
│   │   ├── card_use_cases.py
│   │   └── study_use_cases.py
│   └── services/            # Доменные сервисы
│       └── fsrs_service.py  # Алгоритм интервального повторения
│
├── infrastructure/          # Слой инфраструктуры
│   ├── database/            # База данных
│   │   ├── models/          # SQLAlchemy модели
│   │   └── migrations/      # Миграции Alembic
│   ├── repositories/        # Реализация репозиториев
│   ├── services/            # Внешние сервисы
│   │   ├── import_service.py
│   │   └── tts_service.py
│   ├── security.py          # JWT и хеширование паролей
│   └── config.py            # Конфигурация
│
├── presentation/            # Слой представления
│   ├── api/                 # FastAPI endpoints
│   │   ├── main.py          # Точка входа приложения
│   │   └── routers/         # API роутеры
│   │       ├── users.py
│   │       ├── decks.py
│   │       ├── cards.py
│   │       ├── study.py
│   │       ├── import_router.py
│   │       └── tts_router.py
│   └── schemas/             # Pydantic схемы для валидации
│       ├── user_schemas.py
│       ├── deck_schemas.py
│       ├── card_schemas.py
│       └── study_schemas.py
│
└── tests/                   # Тесты
    ├── conftest.py          # Конфигурация pytest
    ├── test_decks.py
    ├── test_cards.py
    └── test_fsrs.py
```

## Слои архитектуры

### 1. Domain Layer (Доменный слой)

**Ответственность:** Содержит бизнес-логику и правила домена. Не зависит от внешних библиотек и фреймворков.

**Компоненты:**
- **Entities** - Доменные сущности (User, Deck, Card, StudySession)
- **Repositories (интерфейсы)** - Абстрактные интерфейсы для работы с данными

**Принципы:**
- Независим от всех остальных слоев
- Не содержит зависимостей от фреймворков
- Содержит чистую бизнес-логику

### 2. Application Layer (Слой приложения)

**Ответственность:** Реализует use cases (сценарии использования). Координирует работу доменных сущностей и репозиториев.

**Компоненты:**
- **Use Cases** - Конкретные бизнес-сценарии (CreateDeck, ReviewCard, etc.)
- **Services** - Доменные сервисы (FSRS алгоритм)

**Принципы:**
- Зависит только от Domain Layer
- Реализует бизнес-правила через use cases
- Не содержит деталей реализации (БД, HTTP, etc.)

### 3. Infrastructure Layer (Слой инфраструктуры)

**Ответственность:** Реализует технические детали: БД, внешние API, файловые системы.

**Компоненты:**
- **Database Models** - SQLAlchemy ORM модели
- **Repository Implementations** - Конкретная реализация репозиториев
- **External Services** - Интеграции с внешними сервисами (TTS, OCR)
- **Config** - Конфигурация приложения

**Принципы:**
- Реализует интерфейсы из Domain Layer
- Может зависеть от внешних библиотек
- Изолирует технические детали

### 4. Presentation Layer (Слой представления)

**Ответственность:** Обрабатывает HTTP запросы, валидирует входные данные, преобразует их в формат для use cases.

**Компоненты:**
- **Routers** - FastAPI endpoints
- **Schemas** - Pydantic схемы для валидации

**Принципы:**
- Зависит от Application и Domain слоев
- Тонкий слой - только маршрутизация и валидация
- Не содержит бизнес-логики

## Поток данных

```
HTTP Request
    ↓
Presentation Layer (Router)
    ↓
Presentation Layer (Schema validation)
    ↓
Application Layer (Use Case)
    ↓
Domain Layer (Entity / Repository Interface)
    ↓
Infrastructure Layer (Repository Implementation)
    ↓
Database
```

### Создание набора карточек

1. **Presentation Layer** (`decks.py`):
   - Получает HTTP POST запрос
   - Валидирует данные через Pydantic схему
   - Извлекает JWT токен и получает текущего пользователя

2. **Application Layer** (`deck_use_cases.py`):
   - Использует `CreateDeckUseCase`
   - Проверяет существование пользователя
   - Создает доменную сущность `Deck`

3. **Domain Layer** (`deck.py`):
   - `Deck.create()` создает новую сущность с правилами домена

4. **Infrastructure Layer** (`deck_repository.py`):
   - `DeckRepository.create()` сохраняет сущность в БД
   - Преобразует доменную сущность в SQLAlchemy модель

