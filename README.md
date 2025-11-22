# Hooligapps Test Assignment

Fullstack приложение для тестового задания: React frontend + Python FastAPI backend + PostgreSQL.

## Структура проекта

```
.
├── backend/          # Python FastAPI backend
├── frontend/         # React TypeScript frontend
├── docker-compose.yml
└── Makefile          # Основные команды для управления проектом
```

## Быстрый старт

### Запуск всего проекта

```bash
# Запустить все сервисы (включая миграции)
make up

# Или вручную:
docker-compose up -d
docker-compose exec backend poetry run alembic upgrade head
```

### Остановка

```bash
make down
```

## Основные команды

### Управление сервисами

- `make up` - Запустить все сервисы
- `make down` - Остановить все сервисы
- `make build` - Собрать Docker образы
- `make restart` - Перезапустить все сервисы
- `make logs` - Показать логи всех сервисов
- `make logs-backend` - Показать логи backend
- `make logs-frontend` - Показать логи frontend

### Миграции базы данных

- `make migrate` - Применить миграции
- `make migrate-down num=1` - Откатить последнюю миграцию
- `make makemigrations name=migration_name` - Создать новую миграцию

### Тестирование

- `make test` - Запустить все тесты (backend + frontend)
- `make test-backend` - Запустить тесты backend
- `make test-frontend` - Запустить тесты frontend
- `make test-backend-watch` - Запустить тесты backend в watch mode
- `make test-frontend-watch` - Запустить тесты frontend в watch mode

### Frontend

- `make generate-types` - Сгенерировать TypeScript типы из Swagger
- `cd frontend && make dev` - Запустить frontend в dev mode
- `cd frontend && make build` - Собрать frontend для production

### Backend

- `cd backend && make test` - Запустить тесты
- `cd backend && make linter` - Запустить линтер
- `cd backend && make migrate` - Применить миграции

## Технологии

### Backend
- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Pydantic 2+
- Alembic (миграции)

### Frontend
- React 18
- TypeScript
- Vite
- React Router DOM
- Axios
- Vitest + React Testing Library (тесты)

## API Endpoints

- `POST /api/submit` - Отправка формы
- `GET /api/history` - Получение истории с фильтрацией
- `GET /api/unique-names` - Получение уникальных имен и фамилий
- `GET /api/v1/health` - Health check

## Документация

- Backend API: http://localhost:8000/docs (Swagger UI)
- Frontend: http://localhost:3000

## Разработка

### Backend

```bash
cd backend
make install-dev  # Установить зависимости
make test         # Запустить тесты
make linter       # Проверить код
```

### Frontend

```bash
cd frontend
make install      # Установить зависимости
make test         # Запустить тесты
make dev          # Запустить dev server
make generate-types  # Сгенерировать типы из Swagger
```

## Структура страниц

1. **Главная страница** (`/`) - Ссылки на другие страницы
2. **Страница отправки формы** (`/submit`) - Форма с валидацией
3. **Страница истории** (`/history`) - Таблица с фильтрацией

