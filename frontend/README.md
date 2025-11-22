# Frontend - Hooligapps Test

React приложение с TypeScript для тестового задания.

## Технологии

- React 18
- TypeScript
- React Router DOM 6
- Vite
- Axios
- Vitest + React Testing Library (тесты)
- openapi-typescript (для генерации типов из Swagger)

## Быстрый старт

### С Docker (рекомендуется)

```bash
# Из корня проекта
make up  # Запустит все сервисы
```

### Локально

```bash
# Установить зависимости
make install

# Запустить dev server
make dev
```

### Локальная разработка с PyCharm npm

Если npm недоступен в системе, но установлен через PyCharm:

**Создайте файл `frontend/.env.local` (gitignored) с содержимым:**

```bash
NPM_PATH="/Users/job/Library/Application Support/JetBrains/PyCharm2025.2/node/versions/20.19.5/bin/npm"
```

Или установите переменную окружения:

```bash
export NPM_PATH="/Users/job/Library/Application Support/JetBrains/PyCharm2025.2/node/versions/20.19.5/bin/npm"
```

Makefile автоматически обнаружит npm в следующем порядке:
1. Переменная `NPM_PATH` из `.env.local` или окружения
2. Системный npm
3. Docker (только если контейнер запущен)

## Основные команды

См. `Makefile` для всех доступных команд:

- `make install` - Установить зависимости
- `make test` - Запустить тесты
- `make test-watch` - Запустить тесты в watch mode
- `make test-coverage` - Запустить тесты с покрытием
- `make generate-types` - Сгенерировать TypeScript типы из Swagger
- `make build` - Собрать для production
- `make dev` - Запустить dev server

## Генерация типов из Swagger

Типы автоматически генерируются из Swagger документации бэкенда:

```bash
# Убедитесь, что бэкенд запущен
make generate-types
```

Это создаст/обновит файл `src/api/types.ts` с типами на основе OpenAPI схемы бэкенда.

## Структура страниц

- `/` - Главная страница с ссылками
- `/submit` - Страница отправки формы
- `/history` - Страница истории с фильтрацией

## Тестирование

Тесты используют Vitest и React Testing Library:

```bash
make test              # Запустить тесты
make test-watch        # Watch mode
make test-coverage     # С покрытием кода
```
