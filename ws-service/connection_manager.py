"""Connection manager for WebSocket session tracking."""

import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid7

from fastapi import WebSocket

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Represents an active WebSocket session."""

    session_id: str
    websocket: WebSocket
    client_host: str
    client_port: int
    headers: dict[str, str] = field(default_factory=dict)
    query_params: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self):
        self._sessions: dict[str, Session] = {}
        self._is_shutting_down: bool = False

    def connect(
        self,
        websocket: WebSocket,
        client_host: str,
        client_port: int,
        headers: dict[str, str] | None = None,
        query_params: dict[str, str] | None = None,
    ) -> str:
        """Register a new connection and return the session ID."""
        session_id = str(uuid7())
        session = Session(
            session_id=session_id,
            websocket=websocket,
            client_host=client_host,
            client_port=client_port,
            headers=headers or {},
            query_params=query_params or {},
        )
        self._sessions[session_id] = session

        logger.debug(
            "Session registered",
            extra={
                "session_id": session_id,
                "active_sessions": len(self._sessions),
            },
        )

        return session_id

    def disconnect(self, session_id: str) -> None:
        """Remove a connection from tracking."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            logger.debug(
                "Session removed",
                extra={
                    "session_id": session_id,
                    "active_sessions": len(self._sessions),
                },
            )

    def get_session(self, session_id: str) -> Session | None:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def update_metadata(self, session_id: str, metadata: dict[str, Any]) -> None:
        """Update metadata for a session (e.g., Twilio streamSid, callSid)."""
        if session_id in self._sessions:
            self._sessions[session_id].metadata.update(metadata)

    def active_count(self) -> int:
        """Return the number of active connections."""
        return len(self._sessions)

    def begin_shutdown(self) -> None:
        """Mark the manager as shutting down to reject new connections."""
        if not self._is_shutting_down:
            self._is_shutting_down = True
            logger.info(
                "Connection manager entering shutdown mode - rejecting new connections"
            )

    def is_shutting_down(self) -> bool:
        """Check if the manager is in shutdown mode."""
        return self._is_shutting_down

    def get_all_sessions(self) -> list[Session]:
        """Return all active sessions."""
        return list(self._sessions.values())

    async def close_all(self) -> int:
        """Close all active WebSocket connections. Returns count of closed connections."""
        closed_count = 0
        session_ids = list(self._sessions.keys())

        for session_id in session_ids:
            session = self._sessions.get(session_id)
            if session:
                try:
                    await session.websocket.close()
                    closed_count += 1
                except Exception as e:
                    logger.warning(
                        "Error closing WebSocket",
                        extra={
                            "session_id": session_id,
                            "error": str(e),
                        },
                    )
                finally:
                    self.disconnect(session_id)

        return closed_count


# Singleton instance for use across the application
connection_manager = ConnectionManager()
