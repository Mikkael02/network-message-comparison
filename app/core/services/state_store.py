class ResourceNotFoundError(Exception):
    """Raised when a resource does not exist in the state store."""


class InMemoryStateStore:
    def __init__(self) -> None:
        self._values: dict[str, int] = {}

    def set_value(self, resource_id: str, value: int) -> None:
        self._values[resource_id] = value

    def get_value(self, resource_id: str) -> int:
        if resource_id not in self._values:
            raise ResourceNotFoundError(
                f"Resource '{resource_id}' was not found"
            )
        return self._values[resource_id]

    def clear(self) -> None:
        self._values.clear()