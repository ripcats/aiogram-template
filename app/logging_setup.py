import logging

import structlog

from app.config import Config


def setup_logging(config: Config) -> None:
    level = getattr(logging, config.log_level.upper(), logging.INFO)

    shared: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    processors = shared + (
        [structlog.dev.ConsoleRenderer(colors=True)]
        if config.bot_mode == "dev"
        else [structlog.processors.dict_tracebacks, structlog.processors.JSONRenderer()]
    )

    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(format="%(message)s", level=level)
    for lib in ("aiogram", "sqlalchemy.engine", "asyncpg", "aiogram_dialog"):
        logging.getLogger(lib).setLevel(
            logging.DEBUG if config.bot_mode == "dev" else logging.WARNING
        )


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    return structlog.get_logger(name)  # type: ignore[return-value]
