"""Fixed-capacity telemetry history, Section 8.10.3.

300 snapshots at the 200ms cadence is 60 seconds of history, which is what a
reconnecting dashboard replays via ``resume_from``. In-memory only: at 5Hz a
disk-backed buffer would generate write traffic out of proportion to its value,
and the bounded worst case (60s of buffer plus an 8s P1 restart) is accepted in
the methodology.
"""

from __future__ import annotations

from typing import Any, Iterator

from common import protocol


class RingBuffer:
    """Circular buffer of telemetry snapshots, ordered oldest to newest."""

    def __init__(self, capacity: int = protocol.RING_BUFFER_SIZE) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._capacity = capacity
        self._slots: list[dict[str, Any] | None] = [None] * capacity
        self._head = 0  # next write position
        self._count = 0

    def __len__(self) -> int:
        return self._count

    @property
    def capacity(self) -> int:
        return self._capacity

    def append(self, snapshot: dict[str, Any]) -> None:
        self._slots[self._head] = snapshot
        self._head = (self._head + 1) % self._capacity
        if self._count < self._capacity:
            self._count += 1

    def __iter__(self) -> Iterator[dict[str, Any]]:
        start = (self._head - self._count) % self._capacity
        for offset in range(self._count):
            item = self._slots[(start + offset) % self._capacity]
            if item is not None:
                yield item

    def snapshots(self) -> list[dict[str, Any]]:
        return list(self)

    def since(self, last_ts: int, *, limit: int | None = None) -> list[dict[str, Any]]:
        """Snapshots strictly newer than ``last_ts``, oldest first.

        Backs the recovery_batch reply. A client that was away longer than the
        buffer depth gets everything held, and the gap is reported separately
        from the entry list.
        """
        entries = [s for s in self if int(s.get("server_ts", 0)) > int(last_ts)]
        if limit is not None and len(entries) > limit:
            entries = entries[-limit:]
        return entries

    def oldest_ts(self) -> int | None:
        for snapshot in self:
            return int(snapshot.get("server_ts", 0))
        return None

    def newest_ts(self) -> int | None:
        newest: int | None = None
        for snapshot in self:
            newest = int(snapshot.get("server_ts", 0))
        return newest

    def gap_ms(self, last_ts: int) -> int:
        """Milliseconds of history lost for a client resuming from last_ts.

        Zero when the buffer still covers the client's last-seen timestamp;
        otherwise the span between that timestamp and the oldest retained
        snapshot, which the dashboard renders as a map gap marker.
        """
        oldest = self.oldest_ts()
        if oldest is None:
            return 0
        gap = oldest - int(last_ts)
        return gap if gap > 0 else 0

    def clear(self) -> None:
        self._slots = [None] * self._capacity
        self._head = 0
        self._count = 0
