.PHONY: help build up down rm logs shell bot-restart lint fmt typecheck test test-cov

COMPOSE = docker compose
PY_SRC  = app tests
BOT_RUN = $(COMPOSE) run --rm bot

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?##"}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Пересобрать образ бота
	$(COMPOSE) build bot

up: ## Поднять все сервисы
	$(COMPOSE) up -d

down: ## Остановить все сервисы
	$(COMPOSE) down

rm: ## Удалить контейнеры, сеть и volumes проекта
	$(COMPOSE) down -v --remove-orphans

logs: ## Логи бота
	$(COMPOSE) logs -f bot

shell: ## Shell внутри контейнера бота
	$(BOT_RUN) sh

bot-restart: ## Перезапустить только контейнер бота
	$(COMPOSE) restart bot

lint: ## ruff check
	$(BOT_RUN) ruff check $(PY_SRC)

fmt: ## ruff format + fix
	$(BOT_RUN) ruff format $(PY_SRC)
	$(BOT_RUN) ruff check --fix $(PY_SRC)

typecheck: ## mypy
	$(BOT_RUN) mypy $(PY_SRC)

test: ## pytest
	$(BOT_RUN) pytest -v

test-cov: ## pytest + coverage
	$(BOT_RUN) pytest -v --cov=app --cov-report=term-missing
