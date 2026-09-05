"""RingBuffer wraparound and resume_from (since/gap_ms) semantics, Section 8.10.3."""

import pytest

from p1_control.ring_buffer import RingBuffer


def _snapshot(ts: int) -> dict:
    return {"server_ts": ts, "seq": ts}


def test_empty_buffer():
    buf = RingBuffer(capacity=5)
    assert len(buf) == 0
    assert list(buf) == []
    assert buf.oldest_ts() is None
    assert buf.newest_ts() is None
    assert buf.gap_ms(0) == 0


def test_append_and_order_below_capacity():
    buf = RingBuffer(capacity=5)
    for ts in (10, 20, 30):
        buf.append(_snapshot(ts))
    assert len(buf) == 3
    assert [s["server_ts"] for s in buf] == [10, 20, 30]


def test_wraparound_overwrites_oldest():
    buf = RingBuffer(capacity=3)
    for ts in (10, 20, 30, 40, 50):
        buf.append(_snapshot(ts))
    assert len(buf) == 3
    assert [s["server_ts"] for s in buf] == [30, 40, 50]
    assert buf.oldest_ts() == 30
    assert buf.newest_ts() == 50


def test_since_returns_strictly_newer_entries():
    buf = RingBuffer(capacity=10)
    for ts in (10, 20, 30, 40, 50):
        buf.append(_snapshot(ts))
    assert [s["server_ts"] for s in buf.since(20)] == [30, 40, 50]
    assert [s["server_ts"] for s in buf.since(50)] == []
    assert [s["server_ts"] for s in buf.since(0)] == [10, 20, 30, 40, 50]


def test_since_respects_limit_keeping_most_recent():
    buf = RingBuffer(capacity=10)
    for ts in (10, 20, 30, 40, 50):
        buf.append(_snapshot(ts))
    entries = buf.since(0, limit=2)
    assert [s["server_ts"] for s in entries] == [40, 50]


def test_gap_ms_zero_when_buffer_covers_last_seen():
    buf = RingBuffer(capacity=3)
    for ts in (100, 200, 300):
        buf.append(_snapshot(ts))
    assert buf.gap_ms(150) == 0


def test_gap_ms_positive_after_wraparound_evicts_history():
    buf = RingBuffer(capacity=3)
    for ts in (100, 200, 300, 400, 500):
        buf.append(_snapshot(ts))
    # oldest retained is now 300; a client last seen at 150 lost 150ms of history
    assert buf.gap_ms(150) == 150


def test_clear_resets_state():
    buf = RingBuffer(capacity=3)
    for ts in (10, 20, 30):
        buf.append(_snapshot(ts))
    buf.clear()
    assert len(buf) == 0
    assert list(buf) == []


def test_invalid_capacity_raises():
    with pytest.raises(ValueError):
        RingBuffer(capacity=0)
    with pytest.raises(ValueError):
        RingBuffer(capacity=-1)
