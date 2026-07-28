# WalletAPI

FastAPI-приложение для кошельков пользователей, снятия и хранения средств.

## Технологии
 ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
 ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
 ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-005571?style=for-the-badge&logo=sqlalchemy&logoColor=green)
 ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
 ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Быстрый старт

1. Клонируйте репозиторий (или распакуйте проект из архива):
   `git clone https://github.com/MUstinov77/wallet.git`
2. В директории backend cоздайте `.env` на основе `.env.example`
3. Запуск через Docker Desktop:
   `docker compose up --build`
4. Проверка работоспособности:
   откройте `http://0.0.0.0:8000/docs`
5. Создайте пользователя по эндпоинту `http://0.0.0.0:8000/api/v1/auth/signup` — в ответе придёт `api_token`, сохраните его: это единственный раз, когда он возвращается в открытом виде.
6. Для операций с кошельком (`POST /operation`) передавайте токен в заголовке: `Authorization: Bearer <api_token>`.
7. Остановка и очистка:
   `docker compose down -v`

## Переменные окружения

- `DB_USER` - пользователь БД.
- `DB_PASSWORD` - пароль для БД.
- `DB_HOST` - хост БД (имя контейнера с БД).
- `DB_PORT` - порт для подключения к БД.
- `DB_NAME` - имя БД.

## Основные эндпоинты

- `POST /api/v1/auth/signup` — регистрация пользователя, в ответе возвращается `api_token`.
- `GET /api/v1/wallets/?user_id={user_id}` — получение кошелька пользователя.
- `GET /api/v1/wallets/{wallet_id}` — получение кошелька другого пользователя.
- `POST /api/v1/wallets/{wallet_id}/operation` — действия с кошельком. Требует заголовок `Authorization: Bearer <api_token>`; для `WITHDRAW` владельцем кошелька должен быть именно авторизованный пользователь (сверяется с токеном, а не с полем в теле запроса).

## Примечания
- Запуск проверки на стиль синтаксиса `cd backend && flake8`
- Запуск тестов проекта `cd backend && pytest tests/`
- Если при `docker compose up --build` контейнер `app` падает на `alembic upgrade head` с ошибкой `NotNullViolationError: column "hashed_api_token" of relation "users" contains null values` — в volume `db_data` осталась БД со старой схемой (до добавления `hashed_api_token`). Исправляется очисткой volume: `docker compose down -v`, затем `docker compose up --build`.


### Автор проекта [** Максим Устинов**](https://github.com/MUstinov77)