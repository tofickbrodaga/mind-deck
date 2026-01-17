- API документация: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Использование API

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'
```

### Вход в систему
```bash
curl -X POST "http://localhost:8000/api/v1/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

Сохраните полученный `access_token` для дальнейших запросов.

### Создание набора карточек
```bash
curl -X POST "http://localhost:8000/api/v1/decks" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Испанский язык - Базовые слова",
    "description": "Основные испанские слова для начинающих"
  }'
```

### Добавление карточек
```bash
curl -X POST "http://localhost:8000/api/v1/cards/deck/DECK_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "front": "Hola",
    "back": "Привет"
  }'
```

### Получение карточек для повторения
```bash
curl -X GET "http://localhost:8000/api/v1/cards/deck/DECK_ID/due?limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Изучение в режиме флэшкарт
```bash
curl -X GET "http://localhost:8000/api/v1/study/flashcards/DECK_ID?limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Отметить карточку как просмотренную
```bash
curl -X POST "http://localhost:8000/api/v1/cards/CARD_ID/review" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quality": 4
  }'
```

Где `quality` - оценка от 0 до 5:
- 0: Забыл
- 1: Плохо (с подсказкой)
- 2: Хорошо (с усилием)
- 3: Отлично (легко)
- 4: Очень легко
- 5: Слишком легко

## Импорт карточек

### Импорт из Word документа
```bash
curl -X POST "http://localhost:8000/api/v1/import/word/DECK_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@cards.docx"
```

### Импорт из Excel файла
```bash
curl -X POST "http://localhost:8000/api/v1/import/excel/DECK_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@cards.xlsx"
```

### Импорт из изображения (OCR)
```bash
curl -X POST "http://localhost:8000/api/v1/import/image/DECK_ID" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@notes.jpg"
```

## Text-to-Speech

### Генерация аудио для карточки
```bash
curl -X POST "http://localhost:8000/api/v1/tts/card/CARD_ID/generate?language=ru&side=front" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Получить список поддерживаемых языков
```bash
curl -X GET "http://localhost:8000/api/v1/tts/languages"
```

## Режимы обучения

### 1. Флэшкарты (Flashcards)
Перелистывание карточек с просмотром термина и определения.

### 2. Множественный выбор (Multiple Choice)
Выбор правильного ответа из 4 вариантов.

### 3. Письмо (Write)
Ввод определения вручную.

### 4. Подбор (Match)
Сопоставление терминов с определениями.

## Интервальное повторение (FSRS)

MindDeck использует алгоритм FSRS (Free Spaced Repetition Scheduler) для оптимального планирования повторений. Алгоритм автоматически:
- Рассчитывает оптимальные интервалы между повторениями
- Адаптируется к вашему прогрессу
- Приоритизирует карточки, которые нужно повторить

## Тестирование

### Запуск тестов
```bash
docker-compose exec app pytest
```

### Запуск тестов с покрытием
```bash
docker-compose exec app pytest --cov=. --cov-report=html
```
