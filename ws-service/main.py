"""WebSocket service with proper logging and configuration."""

import json
import logging
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from config import settings
from connection_manager import connection_manager
from routes import api_router, websocket_router


# Configure logging based on settings
def setup_logging():
    """Configure logging with appropriate format and level."""

    if settings.log_format == "json":
        # JSON formatter for structured logging
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "module": record.module,
                    "function": record.funcName,
                    "line": record.lineno,
                }

                if record.exc_info:
                    log_data["exception"] = self.formatException(record.exc_info)

                # Add any extra fields
                for key, value in record.__dict__.items():
                    if key not in [
                        "name",
                        "msg",
                        "args",
                        "created",
                        "filename",
                        "funcName",
                        "levelname",
                        "levelno",
                        "lineno",
                        "module",
                        "msecs",
                        "message",
                        "pathname",
                        "process",
                        "processName",
                        "relativeCreated",
                        "thread",
                        "threadName",
                        "exc_info",
                        "exc_text",
                        "stack_info",
                    ]:
                        log_data[key] = value

                return json.dumps(log_data)

        formatter = JsonFormatter()
    else:
        # Text formatter for human-readable logging
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level_int)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.log_level_int)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Set FastAPI and uvicorn loggers to use the same level
    logging.getLogger("fastapi").setLevel(settings.log_level_int)
    logging.getLogger("uvicorn").setLevel(settings.log_level_int)
    logging.getLogger("uvicorn.access").setLevel(settings.log_level_int)


# Setup logging on module import
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Log application startup information.
    logger.info(
        "Application starting",
        extra={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "host": settings.host,
            "port": settings.port,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
        },
    )
    yield
    # Signal shutdown to reject new connections
    logger.info("Initiating graceful shutdown - setting shutdown flag")
    connection_manager.begin_shutdown()

    # Cleanup: close all active WebSocket connections
    active_count = connection_manager.active_count()
    if active_count > 0:
        logger.info(
            "Closing active WebSocket connections",
            extra={"active_sessions": active_count},
        )
        closed_count = await connection_manager.close_all()
        logger.info(
            "WebSocket connections closed", extra={"closed_count": closed_count}
        )

    # Log application shutdown
    logger.info("Application shutting down")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

# Include routers
app.include_router(api_router)
app.include_router(websocket_router)


def main():
    """Main entry point for the application."""
    logger.info(f"Hello from {settings.app_name}!")


if __name__ == "__main__":
    main()
