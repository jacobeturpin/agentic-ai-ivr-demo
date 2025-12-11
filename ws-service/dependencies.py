"""Dependency injection helper functions"""

import logging

from fastapi import Depends, WebSocket, WebSocketDisconnect
from twilio.request_validator import RequestValidator

from config import settings

logger = logging.getLogger(__name__)


def get_twilio_validator() -> RequestValidator:
    return RequestValidator(settings.twilio_auth_token)


async def validate_twilio_websocket(
    websocket: WebSocket,
    validator: RequestValidator = Depends(get_twilio_validator),
) -> None:
    """Dependency that validates Twilio signature on initial websocket handshake

    Can be bypassed for local development using settings.environment = "development"

    Assumes:
    - Twilio media stream connecting with query params including "X-Twilio-Signature"
    - Validation is against the full url + query params according to Twilio docs
    """

    # Bypass validation for development; allows mocking Twilio media stream
    if settings.environment == "development":
        logger.debug("Bypassing Twilio signature validation in development environment")
        return

    headers = websocket.headers
    signature = headers.get("X-Twilio-Signature", None)

    if not signature:
        logger.error(
            "Twilio WebSocket signature missing from headers",
            extra={
                "headers": dict(headers),
            },
        )
        raise WebSocketDisconnect(code=1008)

    # Twilio expects the full URL used in the request *without* the signature param
    # If your signature comes in headers instead, just use websocket.url as-is.
    url_without_sig = str(websocket.url.replace(query=""))

    # Ensure protocol is wss (Twilio requires wss for signature validation)
    if url_without_sig.startswith("ws://"):
        url_without_sig = url_without_sig.replace("ws://", "wss://", 1)

    logger.debug("Validating Twilio WebSocket signature", extra={"url": url_without_sig})

    is_valid = validator.validate(url_without_sig, None, signature)

    if not is_valid:
        # Reject the connection if validation fails
        logger.error("Twilio WebSocket signature validation failed")
        raise WebSocketDisconnect(code=1008)
