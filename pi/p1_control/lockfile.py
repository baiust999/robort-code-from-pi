"""Single-writer enforcement for the Arduino link, Section 8.8.4.2.

An exclusive advisory lock on /run/robot/p1.lock is acquired before any
hardware is opened. /run is tmpfs, so the file never survives a reboot, and the
kernel releases the lock automatically when the holder exits — including on
SIGKILL. This is the first of the layers guaranteeing Invariant VI (exactly one
process writes to the Arduino).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import TracebackType

# flock is POSIX-only; Windows development falls back to msvcrt locking.
if sys.platform == "win32":  # pragma: no cover - dev-host path
    import msvcrt
else:
    import fcntl


class LockAcquisitionError(RuntimeError):
    """Raised when another process already holds the lock."""


class ProcessLock:
    """Exclusive, non-blocking advisory lock held for the process lifetime."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._fd: int | None = None

    def acquire(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            if sys.platform == "win32":  # pragma: no cover - dev-host path
                msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            os.close(fd)
            raise LockAcquisitionError(
                f"{self.path} is held by another process"
            ) from exc

        os.truncate(fd, 0)
        os.write(fd, f"{os.getpid()}\n".encode())
        os.fsync(fd)
        self._fd = fd

    def release(self) -> None:
        if self._fd is None:
            return
        try:
            if sys.platform == "win32":  # pragma: no cover - dev-host path
                os.lseek(self._fd, 0, os.SEEK_SET)
                msvcrt.locking(self._fd, msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(self._fd, fcntl.LOCK_UN)
        except OSError:
            pass  # exiting anyway; the kernel will clean up
        finally:
            os.close(self._fd)
            self._fd = None

    def __enter__(self) -> "ProcessLock":
        self.acquire()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.release()
