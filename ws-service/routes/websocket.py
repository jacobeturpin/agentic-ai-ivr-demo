"""WebSocket routes."""

import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from connection_manager import connection_manager
from models.media_streaming import Message

logger = logging.getLogger(__name__)

router = APIRouter()


def extract_connection_metadata(websocket: WebSocket) -> tuple[str, int, dict[str, str], dict[str, str]]:
    """Extract client metadata from WebSocket connection."""
    client_host = websocket.client.host if websocket.client else "unknown"
    client_port = websocket.client.port if websocket.client else 0

    # Extract relevant headers
    headers = {}
    for key in ["user-agent", "origin", "x-forwarded-for", "x-real-ip"]:
        value = websocket.headers.get(key)
        if value:
            headers[key] = value

    # Extract query parameters
    query_params = dict(websocket.query_params)

    return client_host, client_port, headers, query_params


@router.websocket("/ws/test")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket test endpoint."""
    client_host, client_port, headers, query_params = extract_connection_metadata(websocket)

    await websocket.accept()

    # Register session
    session_id = connection_manager.connect(
        websocket=websocket,
        client_host=client_host,
        client_port=client_port,
        headers=headers,
        query_params=query_params,
    )

    logger.info(
        "WebSocket connection established",
        extra={
            "session_id": session_id,
            "client_host": client_host,
            "client_port": client_port,
            "headers": headers,
            "query_params": query_params,
            "active_sessions": connection_manager.active_count(),
        }
    )

    try:
        while True:
            data = await websocket.receive_text()
            logger.debug(
                "Received WebSocket message",
                extra={
                    "session_id": session_id,
                    "client_host": client_host,
                    "message_length": len(data),
                }
            )

            response = f"Message text was: {data}"
            await websocket.send_text(response)

            logger.debug(
                "Sent WebSocket response",
                extra={
                    "session_id": session_id,
                    "client_host": client_host,
                    "response_length": len(response),
                }
            )
    except WebSocketDisconnect:
        logger.info(
            "WebSocket client disconnected",
            extra={
                "session_id": session_id,
                "client_host": client_host,
                "client_port": client_port,
            }
        )
    except Exception as e:
        logger.error(
            "WebSocket error occurred",
            exc_info=True,
            extra={
                "session_id": session_id,
                "client_host": client_host,
                "error_type": type(e).__name__,
            }
        )
    finally:
        # Cleanup: remove session from tracking
        connection_manager.disconnect(session_id)
        logger.debug(
            "Session cleaned up",
            extra={
                "session_id": session_id,
                "active_sessions": connection_manager.active_count(),
            }
        )

@router.websocket("/ws/media")
async def receive_media(websocket: WebSocket):
    """Receive media from Twilio Media Streaming."""
    client_host, client_port, headers, query_params = extract_connection_metadata(websocket)

    await websocket.accept()

    # Register session
    session_id = connection_manager.connect(
        websocket=websocket,
        client_host=client_host,
        client_port=client_port,
        headers=headers,
        query_params=query_params,
    )

    logger.info(
        "WebSocket connection established",
        extra={
            "session_id": session_id,
            "client_host": client_host,
            "client_port": client_port,
            "headers": headers,
            "query_params": query_params,
            "active_sessions": connection_manager.active_count(),
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
                        "session_id": session_id,
                        "client_host": client_host,
                        "error": str(e),
                        "raw_message": media,
                    }
                )
                continue

            if message.event == "connected":
                logger.info(
                    "Connected Message received",
                    extra={"session_id": session_id, "message": media}
                )
            elif message.event == "start":
                # Extract Twilio metadata from start message
                start_data = media.get("start", {})
                twilio_metadata = {
                    "stream_sid": start_data.get("streamSid"),
                    "call_sid": start_data.get("callSid"),
                    "account_sid": start_data.get("accountSid"),
                }
                connection_manager.update_metadata(session_id, twilio_metadata)
                logger.info(
                    "Start Message received",
                    extra={
                        "session_id": session_id,
                        "message": media,
                        **twilio_metadata,
                    }
                )
            elif message.event == "media":
                if not has_seen_media:
                    logger.info(
                        "Media message",
                        extra={"session_id": session_id, "message": media}
                    )
                    logger.info("Additional media messages from WebSocket are being suppressed....")
                    has_seen_media = True
            elif message.event == "stop":
                logger.info(
                    "Stop Message received",
                    extra={"session_id": session_id, "message": media}
                )
                break

            message_count += 1

        logger.info(
            "Connection closed",
            extra={
                "session_id": session_id,
                "message_count": message_count,
            }
        )
        await websocket.close()

    except WebSocketDisconnect:
        logger.info(
            "WebSocket client disconnected",
            extra={
                "session_id": session_id,
                "client_host": client_host,
                "client_port": client_port,
            }
        )
    except Exception as e:
        logger.error(
            "WebSocket error occurred",
            exc_info=True,
            extra={
                "session_id": session_id,
                "client_host": client_host,
                "error_type": type(e).__name__,
            }
        )
    finally:
        # Cleanup: remove session from tracking
        connection_manager.disconnect(session_id)
        logger.debug(
            "Session cleaned up",
            extra={
                "session_id": session_id,
                "active_sessions": connection_manager.active_count(),
            }
        )



