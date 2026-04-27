from app.core.models.realtime import StateChangeBatch, StateChangeEvent
from app.core.services.state_store import InMemoryStateStore


def get_state_changes_since(
    state_store: InMemoryStateStore,
    last_version: int,
) -> StateChangeBatch:
    events = state_store.get_events_since(last_version)

    return StateChangeBatch(
        from_version=last_version,
        current_version=state_store.get_current_version(),
        events=events,
    )


def seed_demo_state_changes(
    state_store: InMemoryStateStore,
) -> list[StateChangeEvent]:
    generated_events = []

    generated_events.append(state_store.set_value("sensor_01", 10))
    generated_events.append(state_store.set_value("sensor_02", 20))
    generated_events.append(state_store.set_value("sensor_01", 15))

    return generated_events