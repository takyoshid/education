from __future__ import annotations

from .models import Session
from .storage import JsonSessionRepository


def list_sessions(repository: JsonSessionRepository, topic: str | None = None) -> list[Session]:
    sessions = repository.load()
    if topic is not None:
        sessions = [session for session in sessions if session.topic.casefold() == topic.strip().casefold()]
    return sorted(sessions, key=lambda session: (session.started_at, session.session_id))
