"""Wire protocol definitions shared by all Pi processes.

Mirrored by arduino/protocol.h and
dashboard/src/lib/protocol.ts. Changing a constant here means changing it
in both mirrors.

Reference: methodology Sections 8.7.4 (command set), 8.7.5 (telemetry frame),
8.10.1 (WebSocket schemas).
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Any

# --- UART link (P1 <-> Arduino) ---------------------------------------------

SERIAL_BAUD = 115200
GPS_BAUD = 9600

# Arduino boot + handshake timings, Section 8.8.1.2
ARDUINO_BOOT_WAIT_S = 2.0
HANDSHAKE_STOP_REPEATS = 3
HANDSHAKE_STOP_INTERVAL_S = 0.2
HANDSHAKE_READY_TIMEOUT_S = 5.0

READY_TOKEN = "READY"
PANIC_TOKEN = "PANIC"

# Command opcodes, Table 8.7.4. Values are the leading ASCII character.
CMD_FORWARD = "F"
CMD_REVERSE = "R"
CMD_LEFT = "L"
CMD_RIGHT = "G"
CMD_STOP = "S"
CMD_HEARTBEAT = "H"
CMD_PAN = "P"
CMD_TILT = "T"
CMD_STATUS = "?"

# Commands that re-arm the Arduino dead-man timer.
DEADMAN_ARMING_COMMANDS = frozenset(
    {CMD_FORWARD, CMD_REVERSE, CMD_LEFT, CMD_RIGHT, CMD_STOP, CMD_HEARTBEAT}
)
ALL_COMMANDS = frozenset(
    DEADMAN_ARMING_COMMANDS | {CMD_PAN, CMD_TILT, CMD_STATUS}
)

# Dashboard direction token -> Arduino opcode. The dashboard speaks "F/R/L/G"
# already, but routing it through a map keeps the two vocabularies separable.
DIRECTION_TO_OPCODE = {
    "F": CMD_FORWARD,
    "R": CMD_REVERSE,
    "L": CMD_LEFT,
    "G": CMD_RIGHT,
}

MAX_PWM = 180  # caps 14.8V LiPo to ~12V average at the motor, Section 8.7.8
MIN_PWM = 0
SERVO_MIN_ANGLE = 0
SERVO_MAX_ANGLE = 180

MAX_COMMAND_CHARS = 8  # validation stage 1, Figure 8.7.3

# Dead-man window enforced on the Arduino, Section 8.7.6. P1 mirrors the value
# so the mock hardware behaves identically to the real board.
DEADMAN_MS = 2000

# --- Telemetry frame (Arduino -> P1) ----------------------------------------

# Positional CSV, Section 8.7.5. Parsed by index; order is load-bearing.
TELEMETRY_FIELDS: tuple[str, ...] = (
    "temperature_c",
    "humidity_pct",
    "gas_ppm",
    "motion",
    "range_cm",
    "pan_angle",
    "tilt_angle",
    "fw_state",
    "uptime_ms",
)
TELEMETRY_FIELD_COUNT = len(TELEMETRY_FIELDS)
TELEMETRY_MAX_CHARS = 80

# Per-field coercion. A field failing its cast invalidates the whole frame.
TELEMETRY_FIELD_TYPES: dict[str, type] = {
    "temperature_c": float,
    "humidity_pct": float,
    "gas_ppm": int,
    "motion": int,
    "range_cm": int,
    "pan_angle": int,
    "tilt_angle": int,
    "fw_state": int,
    "uptime_ms": int,
}

# Plausibility ranges. Out-of-range means a corrupted frame, Section 8.7.5.
TELEMETRY_FIELD_RANGES: dict[str, tuple[float, float]] = {
    "temperature_c": (-40.0, 125.0),
    "humidity_pct": (0.0, 100.0),
    "gas_ppm": (0, 10000),
    "motion": (0, 1),
    "range_cm": (0, 500),
    "pan_angle": (0, 180),
    "tilt_angle": (0, 180),
    "fw_state": (1, 3),
    "uptime_ms": (0, 2**32 - 1),
}

# Arduino firmware states, Figure 8.7.5.
FW_STATE_ARMED = 1
FW_STATE_DRIVING = 2
FW_STATE_STOPPED = 3

# --- Cadences ---------------------------------------------------------------

TELEMETRY_PERIOD_MS = 200  # Arduino TX and P1 broadcast, Section 8.7.5/8.10.1
HEARTBEAT_PERIOD_MS = 500  # dashboard idle heartbeat, Table 8.15.4
TELEMETRY_LOG_PERIOD_MS = 1000  # disk sampling rate, Section 8.13.2
HEALTH_POLL_PERIOD_S = 10  # P3 -> P1/P2 /health, Section 8.8.3
HEALTH_TIMEOUT_S = 5
HEALTH_FAILURES_BEFORE_KILL = 3
RESTART_COOLDOWN_S = 10  # lock-rejection guard, Section 8.8.3.2

# --- Ring buffer ------------------------------------------------------------

RING_BUFFER_SIZE = 300  # 60s at 200ms, Section 8.10.3

# --- Safety -----------------------------------------------------------------

COMMAND_ACK_TIMEOUT_MS = 3000  # mission state -> STOP, Section 8.11.1.1

# --- Network ----------------------------------------------------------------

P1_PORT = 8080
P2_PORT = 8443
WS_PATH = "/control/ws"
WEBRTC_OFFER_PATH = "/webrtc/offer"

# --- WebSocket message types ------------------------------------------------

# Dashboard -> P1
MSG_MOTOR = "motor"
MSG_SERVO = "servo"
MSG_HEARTBEAT = "heartbeat"
MSG_STOP_ALL = "stop_all"
MSG_HELLO = "hello"
MSG_RESUME_FROM = "resume_from"

# P1 -> dashboard
MSG_TELEMETRY = "telemetry"
MSG_RECOVERY_BATCH = "recovery_batch"
MSG_ACK = "ack"
MSG_ERROR = "error"

CLIENT_MESSAGE_TYPES = frozenset(
    {MSG_MOTOR, MSG_SERVO, MSG_HEARTBEAT, MSG_STOP_ALL, MSG_HELLO, MSG_RESUME_FROM}
)

ROLE_CONTROLLER = "controller"
ROLE_OBSERVER = "observer"

# --- Mission state ----------------------------------------------------------

MISSION_STOP = "STOP"
MISSION_DRIVING_LIMITED = "DRIVING_LIMITED"
MISSION_READY = "READY"
MISSION_DRIVING = "DRIVING"

# --- Alert thresholds (defaults; /etc/robot/thresholds.json overrides) -------

DEFAULT_THRESHOLDS: dict[str, dict[str, float]] = {
    "temperature_c": {"warn": 50.0, "crit": 70.0, "direction": "above"},
    # gas_ppm actually carries the MQ-136's raw ADC count (0-1023), not a
    # calibrated ppm value -- no calibration curve exists for this sensor yet
    # (see arduino/sensors.cpp:readGas). Scaled to line up with the firmware's
    # own alarm point, GAS_ALARM_THRESHOLD in arduino/config.h.
    "gas_ppm": {"warn": 450.0, "crit": 600.0, "direction": "above"},
    "range_cm": {"warn": 30.0, "crit": 20.0, "direction": "below"},
}

# Bit positions for the alert_flags field in telemetry.log, Section 8.13.2.
ALERT_BITS = {
    "temp_warn": 0,
    "temp_crit": 1,
    "gas_warn": 2,
    "gas_crit": 3,
    "range_warn": 4,
    "range_crit": 5,
    "motion": 6,
    "gps_lost": 7,
}


@dataclass
class TelemetrySnapshot:
    """One 200ms telemetry broadcast, Section 8.10.1.2.

    Arduino CSV fields plus GPS, transport status, and server metadata merged
    in by P1. Serialised verbatim as the WebSocket ``telemetry`` payload.
    """

    seq: int = 0
    server_ts: int = 0

    # From the Arduino frame.
    temperature_c: float = 0.0
    humidity_pct: float = 0.0
    gas_ppm: int = 0
    motion: int = 0
    range_cm: int = 0
    pan_angle: int = 90
    tilt_angle: int = 90
    fw_state: int = FW_STATE_ARMED
    uptime_ms: int = 0

    # Merged by P1.
    lat: float | None = None
    lon: float | None = None
    gps_fix: bool = False
    gps_sats: int = 0
    turn_status: str = "unavailable"
    serial_ok: bool = False
    ws_clients: int = 0

    def to_message(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["type"] = MSG_TELEMETRY
        return payload


@dataclass
class ValidationResult:
    """Outcome of the four-stage command pipeline, Figure 8.7.3."""

    ok: bool
    opcode: str | None = None
    argument: int | None = None
    wire: str | None = None
    reason: str | None = None
    warnings: list[str] = field(default_factory=list)


def encode_command(opcode: str, argument: int | None = None) -> str:
    """Render an Arduino wire command, newline-terminated."""
    if opcode not in ALL_COMMANDS:
        raise ValueError(f"unknown opcode {opcode!r}")
    if argument is None:
        return f"{opcode}\n"
    return f"{opcode}{int(argument)}\n"


def parse_telemetry_line(line: str) -> dict[str, Any] | None:
    """Parse one Arduino CSV frame.

    Returns None for any malformed frame — wrong field count, bad cast, or an
    out-of-range value. There is no retransmission; the next frame arrives
    within 200ms (Section 8.7.5), so discarding is the correct response.
    """
    line = line.strip()
    if not line or len(line) > TELEMETRY_MAX_CHARS:
        return None

    parts = line.split(",")
    if len(parts) != TELEMETRY_FIELD_COUNT:
        return None

    parsed: dict[str, Any] = {}
    for name, raw in zip(TELEMETRY_FIELDS, parts):
        caster = TELEMETRY_FIELD_TYPES[name]
        try:
            value = caster(raw)
        except (TypeError, ValueError):
            return None
        low, high = TELEMETRY_FIELD_RANGES[name]
        if not (low <= value <= high):
            return None
        parsed[name] = value
    return parsed


def format_telemetry_line(values: dict[str, Any]) -> str:
    """Inverse of parse_telemetry_line; used by the Arduino emulator."""
    cells = []
    for name in TELEMETRY_FIELDS:
        value = values.get(name, 0)
        if TELEMETRY_FIELD_TYPES[name] is float:
            cells.append(f"{float(value):.1f}")
        else:
            cells.append(str(int(value)))
    return ",".join(cells)


def derive_mission_state(
    *,
    ws_connected: bool,
    serial_ok: bool,
    video_active: bool,
    mesh_ok: bool,
    last_cmd_ack_ms: int,
    command_active: bool,
) -> str:
    """Mission state per Section 8.11.1.1. First matching rule wins."""
    if not ws_connected or not serial_ok or last_cmd_ack_ms > COMMAND_ACK_TIMEOUT_MS:
        return MISSION_STOP
    if not video_active or not mesh_ok:
        return MISSION_DRIVING_LIMITED
    return MISSION_DRIVING if command_active else MISSION_READY


def compute_alert_flags(snapshot: dict[str, Any], thresholds: dict[str, dict[str, float]]) -> int:
    """Pack the telemetry.log alert bitfield, Section 8.13.2."""
    flags = 0

    def _set(bit_name: str) -> None:
        nonlocal flags
        flags |= 1 << ALERT_BITS[bit_name]

    temp = snapshot.get("temperature_c")
    if temp is not None:
        limits = thresholds.get("temperature_c", {})
        if "crit" in limits and temp >= limits["crit"]:
            _set("temp_crit")
        elif "warn" in limits and temp >= limits["warn"]:
            _set("temp_warn")

    gas = snapshot.get("gas_ppm")
    if gas is not None:
        limits = thresholds.get("gas_ppm", {})
        if "crit" in limits and gas >= limits["crit"]:
            _set("gas_crit")
        elif "warn" in limits and gas >= limits["warn"]:
            _set("gas_warn")

    rng = snapshot.get("range_cm")
    if rng is not None:
        limits = thresholds.get("range_cm", {})
        if "crit" in limits and rng <= limits["crit"]:
            _set("range_crit")
        elif "warn" in limits and rng <= limits["warn"]:
            _set("range_warn")

    if snapshot.get("motion"):
        _set("motion")
    if not snapshot.get("gps_fix"):
        _set("gps_lost")

    return flags
