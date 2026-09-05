"""Environment-backed configuration for the Pi processes.

Values come from /etc/robot/*.env on the robot (loaded by systemd) and from
process environment during laptop development. Paths default to ./var on
non-Linux hosts so the stack runs on a dev machine without root.

Reference: methodology Sections 8.13.1.1 (storage layout), 8.14.4 (deployment).
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from . import protocol

_IS_POSIX = sys.platform != "win32"


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_path(name: str, default: Path) -> Path:
    raw = os.environ.get(name)
    return Path(raw) if raw else default


def _default_root() -> Path:
    """/ on the Pi, ./var during development."""
    if _IS_POSIX and Path("/opt/robot").exists():
        return Path("/")
    return Path.cwd() / "var"


@dataclass(frozen=True)
class Paths:
    log_dir: Path
    run_dir: Path
    config_dir: Path
    gps_track_dir: Path

    @classmethod
    def from_env(cls) -> "Paths":
        root = _env_path("ROBOT_ROOT", _default_root())
        if root == Path("/"):
            log_dir = Path("/var/log/robot")
            run_dir = Path("/run/robot")
            config_dir = Path("/etc/robot")
        else:
            log_dir = root / "log"
            run_dir = root / "run"
            config_dir = root / "etc"
        log_dir = _env_path("ROBOT_LOG_DIR", log_dir)
        run_dir = _env_path("ROBOT_RUN_DIR", run_dir)
        config_dir = _env_path("ROBOT_CONFIG_DIR", config_dir)
        return cls(
            log_dir=log_dir,
            run_dir=run_dir,
            config_dir=config_dir,
            gps_track_dir=log_dir / "gps_track",
        )

    def ensure(self) -> None:
        for directory in (self.log_dir, self.run_dir, self.config_dir, self.gps_track_dir):
            directory.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class P1Config:
    """Control server settings, Section 8.8.1."""

    host: str
    port: int
    serial_port: str
    serial_baud: int
    gps_port: str
    gps_baud: int
    mock_hardware: bool
    lock_path: Path
    paths: Paths
    thresholds: dict[str, dict[str, float]]
    stun_url: str
    static_dir: Path | None
    telemetry_log_enabled: bool

    @classmethod
    def from_env(cls) -> "P1Config":
        paths = Paths.from_env()
        mock = _env_bool("MOCK_HARDWARE", not _IS_POSIX)
        static_raw = os.environ.get("DASHBOARD_DIR")
        static_dir = Path(static_raw) if static_raw else None
        if static_dir is not None and not static_dir.exists():
            static_dir = None
        return cls(
            host=os.environ.get("P1_HOST", "0.0.0.0"),
            port=_env_int("P1_PORT", protocol.P1_PORT),
            # Section 8.7.5/8.8 use /dev/ttyUSB0; the 100-page deployment table
            # says /dev/ttyAMA0. Overridable because the correct value depends
            # on whether the Arduino is on USB or the GPIO header.
            serial_port=os.environ.get("SERIAL_PORT", "/dev/ttyUSB0"),
            serial_baud=_env_int("SERIAL_BAUD", protocol.SERIAL_BAUD),
            gps_port=os.environ.get("GPS_PORT", "/dev/serial0"),
            gps_baud=_env_int("GPS_BAUD", protocol.GPS_BAUD),
            mock_hardware=mock,
            lock_path=_env_path("P1_LOCK", paths.run_dir / "p1.lock"),
            paths=paths,
            thresholds=load_thresholds(paths.config_dir),
            stun_url=os.environ.get("STUN_URL", "stun:192.168.10.1:3478"),
            static_dir=static_dir,
            telemetry_log_enabled=_env_bool("TELEMETRY_LOG", True),
        )


@dataclass(frozen=True)
class P2Config:
    """Media server settings, Section 8.8.2."""

    host: str
    port: int
    mock_hardware: bool
    video_device: str
    audio_device: str
    width: int
    height: int
    framerate: int
    bitrate_kbps: int
    paths: Paths

    @classmethod
    def from_env(cls) -> "P2Config":
        return cls(
            host=os.environ.get("P2_HOST", "0.0.0.0"),
            port=_env_int("P2_PORT", protocol.P2_PORT),
            mock_hardware=_env_bool("MOCK_HARDWARE", not _IS_POSIX),
            video_device=os.environ.get("VIDEO_DEVICE", "/dev/video0"),
            audio_device=os.environ.get("AUDIO_DEVICE", "default"),
            width=_env_int("VIDEO_WIDTH", 640),
            height=_env_int("VIDEO_HEIGHT", 480),
            framerate=_env_int("VIDEO_FPS", 10),
            bitrate_kbps=_env_int("VIDEO_BITRATE_KBPS", 500),
            paths=Paths.from_env(),
        )


@dataclass(frozen=True)
class P3Config:
    """Watchdog settings, Section 8.8.3."""

    p1_cmd: list[str]
    p2_cmd: list[str]
    p1_health_url: str
    p2_health_url: str
    enable_overlay: bool
    mesh_gateway: str
    paths: Paths

    @classmethod
    def from_env(cls) -> "P3Config":
        python = os.environ.get("PYTHON_BIN", sys.executable)
        return cls(
            p1_cmd=_split_cmd(os.environ.get("P1_CMD"), [python, "-m", "p1_control.main"]),
            p2_cmd=_split_cmd(os.environ.get("P2_CMD"), [python, "-m", "p2_media.main"]),
            p1_health_url=os.environ.get(
                "P1_HEALTH_URL", f"http://127.0.0.1:{protocol.P1_PORT}/health"
            ),
            p2_health_url=os.environ.get(
                "P2_HEALTH_URL", f"http://127.0.0.1:{protocol.P2_PORT}/health"
            ),
            enable_overlay=_env_bool("ENABLE_OVERLAY", False),
            mesh_gateway=os.environ.get("MESH_GATEWAY", "192.168.10.1"),
            paths=Paths.from_env(),
        )


def _split_cmd(raw: str | None, default: list[str]) -> list[str]:
    if not raw:
        return default
    import shlex

    return shlex.split(raw)


def load_thresholds(config_dir: Path) -> dict[str, dict[str, float]]:
    """Read thresholds.json, falling back to the spec defaults."""
    path = config_dir / "thresholds.json"
    thresholds = {k: dict(v) for k, v in protocol.DEFAULT_THRESHOLDS.items()}
    try:
        with path.open("r", encoding="utf-8") as handle:
            override = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return thresholds
    for key, limits in override.items():
        if isinstance(limits, dict):
            thresholds.setdefault(key, {}).update(limits)
    return thresholds
