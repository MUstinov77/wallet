# Selectel Vacancies API

FastAPI-приложение для кошельков пользователей, снятия и хранения средств.

## Технологии
 ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
 ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
 ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-005571?style=for-the-badge&logo=sqlalchemy&logoColor=green)
 ![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
 ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Быстрый старт

1. Клонируйте репозиторий (или распакуйте проект из архива):
   `git clone --branch with-bugs https://github.com/selectel/be-test.git`
2. В директории backend Создайте `.env` на основе примера:
   `cp .env.example .env`
3. Запуск через Docker Desktop:
   `docker compose up --build`
4. Проверка работоспособности:
   откройте `http://0.0.0.0:8000/docs`
5. Создайте пользователя по эндпоинту `http://0.0.0.0:8000/api/v1/auth/signup`
6. Авторизуйтесь воспользовавшись кнопкой Authorize. (все энпоинты работают только для авторизованных пользователей)
7. Остановка и очистка:
   `docker-compose down -v`

## Переменные окружения

- `AUTH_SERCRET_KEY` — ключ для подписи токенов доступа. (для генерации ключа в теминале `openssl rang -hex 32`)
- `JWT_ALGORITM` — алгоритм для генерации и расшифровки токена доступа.
- `JWT_ISSUER` — кем выдан токен.
- `TOKEN_EXPIRE_HOURS` — срок действия токена.
- `DB_USER` - пользователь БД.
- `DB_PASSWORD` - пароль для БД.
- `DB_HOST` - хост БД (имя контейнера с БД).
- `DB_PORT` - порт для подключения к БД.
- `DB_NAME` - имя БД.

## Основные эндпоинты

- `POST /api/v1/auth/singup/` — регистрация пользователя
- `POST /api/v1/auth/login/` — получение токена доступа.
- `GET /api/v1/wallets/` — получение собственного кошелька.
- `GET /api/v1/wallets/{wallet_id}` — получение кошелька друго пользователя.
- `POST /api/v1/wallets/{wallet_id}/operation/` — действия с кошельком.

## Примечания
- Запуск проверки на стиль синтаксиса `cd backend && flake8`
- Запуск тестов проекта `cd backend && pytest tests/`


### Автор проекта [** Максим Устинов**](https://github.com/MUstinov77)