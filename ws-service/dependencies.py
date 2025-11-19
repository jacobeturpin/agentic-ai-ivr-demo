"""Dependency injection helper functions"""
from fastapi import Depends, WebSocket, WebSocketDisconnect
from twilio.request_validator import RequestValidator

from config import settings


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
        return

    query_params = websocket.query_params
    signature = query_params.get("X-Twilio-Signature", None)

    if not signature:
        raise WebSocketDisconnect(code = 1008)
    
    # Twilio expects the full URL used in the request *without* the signature param
    # If your signature comes in headers instead, just use websocket.url as-is.
    url_without_sig = str(websocket.url.replace(query=""))

    is_valid = validator.validate(url_without_sig, query_params, signature)

    if not is_valid:
        # Reject the connection if validation fails
        raise WebSocketDisconnect(code=1008)
