"""Controller key check with per-host lockout.

Only a dashboard that presents the robot's controller key (``CONTROLLER_KEY``
in /etc/robot/p1.env) may drive the robot or talk to the victim; everyone
else is a view-only observer. P1 and P2 each hold a ``KeyGate``.

The key may be short, so repeated wrong guesses from one host lock that host
out: after ``max_failures`` wrong keys within ``lockout_s`` it is refused
(even with the right key) until ``lockout_s`` has passed. Each process keeps
its own counters, in memory; restarting the service clears them.
"""

from __future__ import annotations

import hmac
import math
import time
from typing import Callable

# check() verdicts, also sent to the dashboard so it can say why.
OK = "ok"
NO_KEY = "no_key"
BAD_KEY = "bad_key"
LOCKED = "locked"
DISABLED = "disabled"  # no CONTROLLER_KEY configured: nobody may control

MAX_FAILURES = 5
LOCKOUT_S = 300.0


class KeyGate:
    """Checks presented controller keys and locks out hosts that guess."""

    def __init__(
        self,
        key: str,
        *,
        max_failures: int = MAX_FAILURES,
        lockout_s: float = LOCKOUT_S,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._key = key.encode()
        self.max_failures = max_failures
        self.lockout_s = lockout_s
        self._clock = clock
        self._failures: dict[str, list[float]] = {}
        self._locked_until: dict[str, float] = {}

    @property
    def enabled(self) -> bool:
        return bool(self._key)

    def retry_after(self, host: str) -> int:
        """Whole seconds until ``host``'s lockout ends (0 if not locked)."""
        until = self._locked_until.get(host)
        if until is None:
            return 0
        return max(0, math.ceil(until - self._clock()))

    def check(self, host: str, presented: str | None) -> str:
        # Connecting without a key is how an observer joins, not a guess.
        if not presented:
            return NO_KEY

        now = self._clock()
        until = self._locked_until.get(host)
        if until is not None:
            if now < until:
                return LOCKED
            del self._locked_until[host]
        if not self._key:
            return DISABLED
        if hmac.compare_digest(presented.encode(), self._key):
            self._failures.pop(host, None)
            return OK

        recent = [t for t in self._failures.get(host, []) if now - t < self.lockout_s]
        recent.append(now)
        if len(recent) >= self.max_failures:
            self._failures.pop(host, None)
            self._locked_until[host] = now + self.lockout_s
            return LOCKED
        self._failures[host] = recent
        return BAD_KEY
