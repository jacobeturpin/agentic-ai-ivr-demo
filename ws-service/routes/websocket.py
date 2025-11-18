"""WebSocket routes."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from models.media_streaming import Message

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

@router.websocket('ws/media')
async def receive_media(websocket: WebSocket):
    """Receive media from Twilio Media Streaming"""
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
        message_count = 0
        has_seen_media = False

        while True:
            media = await websocket.receive_json()

            # Validate message against defined types
            try:
                message = Message.model_validate(media)
            except ValidationError as e:
                logger.warning(
                    "Invalid message format, dropping",
                    extra={
                        "client_host": client_host,
                        "error": str(e),
                        "raw_message": media,
                    }
                )
                continue

            if message.event == "connected":
                logger.info("Connected Message received", extra={"message": media})
            elif message.event == "start":
                logger.info("Start Message received", extra={"message": media})
            elif message.event == "media":
                if not has_seen_media:
                    logger.info("Media message", extra={"message": media})
                    logger.info("Additional media messages from WebSocket are being suppressed....")
                    has_seen_media = True
            elif message.event == "stop":
                logger.info("Stop Message received", extra={"message": media})
                break

            message_count += 1

        logger.info("Connection closed. Received a total of {} messages".format(message_count))
        await websocket.close()

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



