# WalletAPI

FastAPI-приложение для кошельков: хранение, пополнение и снятие средств.

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
5. Создайте кошелёк по эндпоинту `POST http://0.0.0.0:8000/api/v1/wallets/` — в ответе придёт `id` кошелька, сохраните его: он используется во всех дальнейших запросах к этому кошельку.
6. Остановка и очистка:
   `docker compose down -v`

## Переменные окружения

- `DB_USER` - пользователь БД.
- `DB_PASSWORD` - пароль для БД.
- `DB_HOST` - хост БД (имя контейнера с БД).
- `DB_PORT` - порт для подключения к БД.
- `DB_NAME` - имя БД.

## Авторизация

⚠️ В проекте нет пользователей, аутентификации или авторизации: кошелёк ничей, и **любой, кто знает `wallet_id`, может снять с него деньги** (`POST /operation` с `WITHDRAW`), а не только пополнить. Единственный контроль — проверка баланса (нельзя увести его в минус). Относитесь к `wallet_id` как к секрету и не раскрывайте его.

## Основные эндпоинты

- `POST /api/v1/wallets/` — создание кошелька с нулевым балансом, в ответе возвращается `id` кошелька.
- `GET /api/v1/wallets/{wallet_id}` — получение кошелька по идентификатору.
- `POST /api/v1/wallets/{wallet_id}/operation` — пополнение (`DEPOSIT`) или снятие (`WITHDRAW`) средств. Тело запроса: `{"operation_type": "DEPOSIT"|"WITHDRAW", "amount": "10.00"}`. Проверки владельца нет: снять деньги может любой, кто знает `wallet_id`.

## Примечания
- Запуск проверки на стиль синтаксиса `cd backend && flake8`
- Запуск тестов проекта `cd backend && pytest tests/`
- Если при `docker compose up --build` контейнер `app` падает на `alembic upgrade head` с ошибкой несоответствия схемы — в volume `db_data` осталась БД со старой схемой. Исправляется очисткой volume: `docker compose down -v`, затем `docker compose up --build`.


### Автор проекта [** Максим Устинов**](https://github.com/MUstinov77)