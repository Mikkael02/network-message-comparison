from datetime import datetime, timezone

from app.core.models.realtime import StateChangeEvent


class ResourceNotFoundError(Exception):
    """Raised when a resource does not exist in the state store."""


class InMemoryStateStore:
    def __init__(self) -> None:
        self._values: dict[str, int] = {}
        self._version: int = 0
        self._events: list[StateChangeEvent] = []

    def set_value(self, resource_id: str, value: int) -> StateChangeEvent:
        self._version += 1
        self._values[resource_id] = value

        event = StateChangeEvent(
            version=self._version,
            timestamp=datetime.now(timezone.utc),
            resource_id=resource_id,
            value=value,
        )
        self._events.append(event)
        return event

    def get_value(self, resource_id: str) -> int:
        if resource_id not in self._values:
            raise ResourceNotFoundError(
                f"Resource '{resource_id}' was not found"
            )
        return self._values[resource_id]

    def get_current_version(self) -> int:
        return self._version

    def get_events_since(self, last_version: int) -> list[StateChangeEvent]:
        if last_version < 0:
            raise ValueError("last_version cannot be negative")

        return [event for event in self._events if event.version > last_version]

    def get_snapshot(self) -> dict[str, int]:
        return dict(self._values)

    def clear(self) -> None:
        self._values.clear()
        self._events.clear()
        self._version = 0