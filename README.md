<div align="center">

# aiogram-template

Лёгкий шаблон для Telegram-ботов на `aiogram 3` с `FastAPI`, `SQLAlchemy`, `Redis` и `Dishka`.

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2ea44f.svg)](https://github.com/aiogram/aiogram)
[![FastAPI](https://img.shields.io/badge/FastAPI-webhook-009688.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17--alpine-336791.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-8--alpine-dc382d.svg)](https://redis.io/)
[![Dishka](https://img.shields.io/badge/Dishka-DI-1f6feb.svg)](https://github.com/reagento/dishka)
[![Docker](https://img.shields.io/badge/docker-compose-2496ed.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-black.svg)](./LICENSE)

> Минимум лишнего. Нормальная база для реального бота.

</div>

---

## Что внутри

- **Два режима**: polling для разработки, webhook для прода — из одной кодовой базы
- **PostgreSQL + Redis** подняты через Docker Compose, таблицы создаются при старте
- **Dependency Injection** через `Dishka` — чисто, без глобальных состояний
- **Слоистая архитектура**: domain / application / infrastructure / presentation
- **`aiogram-dialog`** включён по умолчанию и легко удаляется одной командой
- **`config.json`** для прикладных настроек, `.env` для окружения

---

## Быстрый старт

```bash
git clone https://github.com/ripcats/aiogram-template.git
cd aiogram-template
cp .env.example .env
# заполни .env
make up
make logs
```

Склонировал → заполнил `.env` → поднял стек → начал писать логику.

---

## Использование как GitHub Template

1. Нажми **Use this template** → создай новый репозиторий
2. Склонируй локально
3. Заполни `.env`
4. Запусти `make up`

---

## Структура

```
app/
├── application/        # use cases, DTO, сервисы
├── domain/             # сущности, исключения, контракты
├── infrastructure/     # репозитории, cache, db, IoC
├── presentation/       # handlers, dialogs, filters, middlewares
├── ui/                 # тексты и кнопки (messages.json)
├── config.py
├── logging_setup.py
└── main.py
```

Зависимости между слоями:

```
presentation   → application → domain
infrastructure → application → domain
```

---

## Режимы работы

### `bot_mode=dev` — polling

```env
bot_mode=dev
bot_token=123456:token
bot_owner_id=123456789
log_level=INFO

postgres_host=postgres
postgres_port=5432
postgres_user=bot
postgres_password=botpass
postgres_db=botdb

redis_host=redis
redis_port=6379
redis_db=0
```

`bot_webhook_host` и `bot_webhook_secret` не нужны.

### `bot_mode=prod` — webhook

```env
bot_mode=prod
bot_token=123456:token
bot_owner_id=123456789
log_level=INFO

bot_webhook_host=https://bot.example.com
bot_webhook_path=/webhook
bot_webhook_secret=secret

server_host=0.0.0.0
server_port=8080

postgres_host=postgres
postgres_port=5432
postgres_user=bot
postgres_password=botpass
postgres_db=botdb

redis_host=redis
redis_port=6379
redis_db=0
```

---

## Webhook + nginx

В `prod` режиме `FastAPI` слушает `server_host:server_port` внутри контейнера `bot`.

Типовая схема:

```
Telegram → HTTPS → nginx → http://bot:8080/webhook → FastAPI
```

`server_host` должен быть `0.0.0.0`, чтобы nginx или Docker network могли достучаться.

Хост по умолчанию: `0.0.0.0`.  
Порт по умолчанию: `8080`.

Публичный webhook URL собирается из `bot_webhook_host` + `bot_webhook_path`.

---

## Команды

```bash
make build          # сборка образов
make up             # запуск стека
make down           # остановка
make rm             # остановка + удаление контейнеров
make logs           # логи
make shell          # shell внутри контейнера бота
make bot-restart    # перезапуск только бота

make lint           # линтер
make fmt            # форматирование
make typecheck      # проверка типов
make test           # тесты
make test-cov       # тесты с покрытием
```

---

## config.json

Прикладные настройки, которые не относятся к запуску окружения:

| Ключ | Описание |
|---|---|
| `owner_panel.users_per_page` | пагинация в панели владельца |
| `rate_limit.limit` | лимит запросов |
| `rate_limit.window_seconds` | окно ограничения |
| `ban_cache.key_prefix` | префикс ключа в Redis |
| `ban_cache.ttl_seconds` | TTL записи о бане |
| `ban_cache.refresh_threshold_seconds` | порог обновления |
| `ban_cache.refresh_extension_seconds` | продление при обновлении |

---

## Удаление aiogram-dialog

Если диалоговый flow не нужен — вычищается одной командой:

```bash
# Linux / macOS
./dialog_rem.sh

# Windows
./dialog_rem.ps1
```

Скрипт удалит:

- зависимость из `pyproject.toml`
- startup-подключение из `app/main.py`
- папку `app/presentation/dialogs`
- логгер `aiogram_dialog` из `app/logging_setup.py`

---

## Как расширять

Новая фича добавляется по слоям:

1. **`domain`** — сущности, исключения, контракты
2. **`application`** — DTO, use case, сервисы
3. **`infrastructure`** — репозитории, cache, db
4. **`presentation`** — handlers, dialogs, filters, middlewares
5. **`ui`** — тексты и кнопки в `messages.json`

Минимальный путь для новой фичи:

- добавить use case
- подключить в `app/infrastructure/ioc/providers.py`
- добавить handler или dialog
- зарегистрировать router
- вынести тексты в `app/ui/messages.json`

---

## Обратная связь

Нашёл баг, хочешь задать вопрос или предложить улучшение — создай [issue](https://github.com/ripcats/aiogram-template/issues).

---

<div align="center">

Сделано **Evgeny Gerber** · [t.me/ripcats](https://t.me/ripcats) · pm@c8evgeny.ru

[![GitHub Issues](https://img.shields.io/badge/GitHub-Issues-1f2328.svg)](https://github.com/ripcats/aiogram-template/issues)
&nbsp;
[![License: MIT](https://img.shields.io/badge/license-MIT-black.svg)](./LICENSE)

</div>
