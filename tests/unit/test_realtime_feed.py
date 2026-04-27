import pytest

from app.core.services.realtime_feed import (
    get_state_changes_since,
    seed_demo_state_changes,
)
from app.core.services.state_store import InMemoryStateStore


def test_state_store_records_versioned_events():
    store = InMemoryStateStore()

    event_1 = store.set_value("sensor_01", 10)
    event_2 = store.set_value("sensor_01", 20)

    assert event_1.version == 1
    assert event_2.version == 2
    assert store.get_current_version() == 2
    assert store.get_value("sensor_01") == 20


def test_get_events_since_returns_only_newer_events():
    store = InMemoryStateStore()

    store.set_value("sensor_01", 10)
    store.set_value("sensor_02", 20)
    store.set_value("sensor_01", 15)

    events = store.get_events_since(1)

    assert len(events) == 2
    assert events[0].version == 2
    assert events[1].version == 3
    assert events[0].resource_id == "sensor_02"
    assert events[1].resource_id == "sensor_01"


def test_get_state_changes_since_returns_batch():
    store = InMemoryStateStore()

    store.set_value("sensor_01", 10)
    store.set_value("sensor_02", 20)

    batch = get_state_changes_since(store, 0)

    assert batch.from_version == 0
    assert batch.current_version == 2
    assert len(batch.events) == 2
    assert batch.events[0].version == 1
    assert batch.events[1].version == 2


def test_get_state_changes_since_for_up_to_date_version_returns_empty_batch():
    store = InMemoryStateStore()

    store.set_value("sensor_01", 10)
    current_version = store.get_current_version()

    batch = get_state_changes_since(store, current_version)

    assert batch.from_version == current_version
    assert batch.current_version == current_version
    assert batch.events == []


def test_clear_resets_values_versions_and_events():
    store = InMemoryStateStore()

    store.set_value("sensor_01", 10)
    store.set_value("sensor_02", 20)

    store.clear()

    assert store.get_current_version() == 0
    assert store.get_events_since(0) == []
    assert store.get_snapshot() == {}


def test_seed_demo_state_changes_populates_store():
    store = InMemoryStateStore()

    events = seed_demo_state_changes(store)

    assert len(events) == 3
    assert store.get_current_version() == 3
    assert store.get_value("sensor_01") == 15
    assert store.get_value("sensor_02") == 20


def test_get_events_since_rejects_negative_version():
    store = InMemoryStateStore()

    with pytest.raises(ValueError):
        store.get_events_since(-1)