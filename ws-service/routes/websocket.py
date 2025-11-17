"""WebSocket routes."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/test")
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
