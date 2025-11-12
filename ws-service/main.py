"""WebSocket service with proper logging and configuration."""
import json
import logging
import sys
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from config import settings

# Configure logging based on settings
def setup_logging():
    """Configure logging with appropriate format and level."""

    if settings.log_format == "json":
        # JSON formatter for structured logging
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_data = {
                    "timestamp": datetime.utcnow().isoformat(),
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
                    if key not in ["name", "msg", "args", "created", "filename", "funcName",
                                   "levelname", "levelno", "lineno", "module", "msecs",
                                   "message", "pathname", "process", "processName",
                                   "relativeCreated", "thread", "threadName", "exc_info",
                                   "exc_text", "stack_info"]:
                        log_data[key] = value

                return json.dumps(log_data)

        formatter = JsonFormatter()
    else:
        # Text formatter for human-readable logging
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
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

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


@app.on_event("startup")
async def startup_event():
    """Log application startup information."""
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
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down")


@app.get("/")
def read_root():
    """Health check endpoint."""
    logger.debug("Health check endpoint called")
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "healthy",
        "environment": settings.environment,
    }


@app.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket test endpoint."""
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0

    await websocket.accept()
    logger.info(
        "WebSocket connection established",
        extra={
            "client_host": client_host,
            "client_port": client_port,
        }
    )

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(
                "Received WebSocket message",
                extra={
                    "client_host": client_host,
                    "message_length": len(data),
                }
            )

            response = f"Message text was: {data}"
            await websocket.send_text(response)

            logger.debug(
                "Sent WebSocket response",
                extra={
                    "client_host": client_host,
                    "response_length": len(response),
                }
            )
    except WebSocketDisconnect:
        logger.info(
            "WebSocket client disconnected",
            extra={
                "client_host": client_host,
                "client_port": client_port,
            }
        )
    except Exception as e:
        logger.error(
            "WebSocket error occurred",
            exc_info=True,
            extra={
                "client_host": client_host,
                "error_type": type(e).__name__,
            }
        )


def main():
    """Main entry point for the application."""
    logger.info(f"Hello from {settings.app_name}!")


if __name__ == "__main__":
    main()
