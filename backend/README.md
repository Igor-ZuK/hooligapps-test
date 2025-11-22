# Backend - Hooligapps Test

Python FastAPI backend для тестового задания.

## Технологии

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- Pydantic 2+
- Alembic (миграции)
- Poetry (управление зависимостями)

## Быстрый старт

### С Docker (рекомендуется)

```bash
# Из корня проекта
make up  # Запустит все сервисы включая миграции
```

### Локально

```bash
# Установить зависимости
make install-dev

# Запустить сервер
python main.py
```

## Основные команды

См. `Makefile` для всех доступных команд:

- `make install` - Установить зависимости
- `make install-dev` - Установить зависимости + dev tools
- `make test` - Запустить тесты
- `make linter` - Запустить линтер (ruff + mypy)
- `make migrate` - Применить миграции
- `make makemigrations name=name` - Создать новую миграцию

## API Endpoints

- `POST /api/submit` - Отправка формы
- `GET /api/history` - Получение истории с фильтрацией
- `GET /api/unique-names` - Получение уникальных имен и фамилий
- `GET /api/v1/health` - Health check

## Документация

Swagger UI доступен на: http://localhost:8000/docs

## Структура проекта

```
backend/
├── project/
│   ├── apps/          # Приложения (history, service)
│   ├── core/          # Ядро приложения (settings, db, uc, middlewares)
│   └── ...
├── tests/             # Тесты
├── migrations/        # Миграции Alembic
└── Makefile          # Команды для разработки
```
