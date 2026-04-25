# Информационная система управления ПМСП в сельских территориях

MVP-проект на Django для ведения прикрепленного населения, обращений, выездов на дом, профилактики, направлений и простой управленческой аналитики для сельской первичной медико-санитарной помощи.

## Стек

- Python 3.12
- Django 5.2
- PostgreSQL
- Django Templates
- HTMX
- Bootstrap 5.3
- Gunicorn
- Docker Compose
- pytest
- Ruff

## Реализованные модули

- `core`: dashboard, уведомления, общие шаблоны, ошибки 403/404/500
- `accounts`: профили сотрудников, роли, RBAC, demo users
- `facilities`: учреждения
- `patients`: реестр пациентов, поиск, фильтры, карточка, CRUD, CSV
- `encounters`: обращения, фильтры, CRUD, CSV
- `visits`: выезды на дом, несколько пациентов в одном выезде, страница на сегодня
- `prevention`: профилактика и диспансеризация, overdue, CSV
- `referrals`: направления, смена статусов, CSV
- `reports`: dashboard и фоновая генерация уведомлений
- `audit`: журнал аудита ключевых действий

## Локальный запуск без Docker

1. Создайте виртуальное окружение на Python 3.12.
2. Установите зависимости: `pip install -e .[dev]`
3. Скопируйте `.env.example` в `.env`
4. Поднимите PostgreSQL или укажите внешний `DATABASE_URL`
5. Выполните миграции: `python manage.py migrate`
6. Создайте демо-пользователей: `python manage.py create_demo_users`
7. Загрузите демо-данные: `python manage.py seed_demo_data`
8. Запустите сервер: `python manage.py runserver`

## Запуск через Docker Compose

1. Скопируйте `.env.example` в `.env`
2. Запустите: `docker compose up --build`
3. В отдельном терминале при необходимости загрузите демо-данные:
   `docker compose exec web python manage.py seed_demo_data`
4. Приложение будет доступно на `http://localhost:8000`

## Миграции и суперпользователь

- Применить миграции: `python manage.py migrate`
- Создать суперпользователя: `python manage.py createsuperuser`
- Сгенерировать уведомления: `python manage.py generate_notifications`

## Demo logins/passwords

- `admin / demo12345`
- `registrator / demo12345`
- `doctor / demo12345`
- `manager / demo12345`

После `seed_demo_data` также появятся дополнительные тестовые пользователи.

## Внешняя PostgreSQL / Supabase

Проект поддерживает подключение через `DATABASE_URL`. Если переменная задана, Django использует внешний PostgreSQL без изменения кода.

Пример:

```env
DATABASE_URL=postgresql://postgres:password@db.example.com:5432/rural_pmsp
```

Для Supabase используйте connection string базы Supabase в этом же формате. Локальный сервис `db` в `docker-compose.yml` при этом можно отключить.

## Тесты и линтинг

- Запуск тестов: `pytest`
- Линтинг: `ruff check .`

Для тестов используется отдельный settings-модуль `config.settings.test` на SQLite, чтобы прогон был быстрым.

## Структура проекта

```text
manage.py
pyproject.toml
docker-compose.yml
Dockerfile
.env.example
config/
apps/
templates/
static/
tests/
deploy/nginx.conf
```

## Ограничения MVP

- Нет интеграций с внешними гос. системами
- Нет SMS/email-уведомлений
- Нет телемедицины, лабораторий, рецептов и billing
- Нет мобильного приложения и offline sync
- Аналитика ограничена dashboard и CSV-экспортом
