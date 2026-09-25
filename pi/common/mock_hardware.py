"""Software emulation of the Arduino board and the NEO-6M GPS.

Enabled with MOCK_HARDWARE=1. The emulator implements the firmware's
framing/opcode/argument-clamp validation, dead-man timer, and telemetry
cadence closely enough that P1 cannot tell it apart from a real board across
the serial boundary for driving and telemetry purposes; it does not model the
firmware's ESTOP/PANIC state-machine gate, since the mock has no fault
states. This is what lets the full stack run on a development machine.

Reference: arduino/ — behaviour mirrored from there.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field

from . import protocol


@dataclass
class _MotorState:
    speed: int = 0
    direction: str | None = None


class MockArduino:
    """Emulates the UNO firmware over an in-memory serial interface."""

    def __init__(self, *, seed: int | None = None) -> None:
        self._rng = random.Random(seed)
        self._boot_ms = _now_ms()
        self._rx = bytearray()
        self._tx = bytearray()
        self._motors = _MotorState()
        self._pan = 90
        self._tilt = 90
        self._fw_state = protocol.FW_STATE_ARMED
        # Dead-man starts expired, matching stateInit() in robot_state.cpp.
        self._last_command_ms = _now_ms() - (protocol.DEADMAN_MS + 1)
        self._deadman_tripped = True
        self._last_telemetry_ms = 0.0
        self._motion_latch = 0

        # Simulated environment.
        self._temperature = 24.5
        self._humidity = 55.0
        self._gas = 3
        self._range_cm = 180
        self._next_motion_ms = _now_ms() + self._rng.uniform(4000, 12000)

        self._tx.extend((protocol.READY_TOKEN + "\n").encode())

    # --- serial-facing surface ---------------------------------------------

    def write(self, data: bytes) -> int:
        self._rx.extend(data)
        self._drain_commands()
        return len(data)

    def read_all(self) -> bytes:
        self.tick()
        out = bytes(self._tx)
        self._tx.clear()
        return out

    def reset_buffers(self) -> None:
        self._rx.clear()
        self._tx.clear()

    def pulse_dtr(self) -> None:
        """Emulate the DTR-triggered board reset on serial open."""
        self.__init__(seed=self._rng.randint(0, 2**31))  # noqa: PLC2801

    # --- simulation ---------------------------------------------------------

    def tick(self) -> None:
        now = _now_ms()
        self._check_deadman(now)
        self._advance_environment(now)
        if now - self._last_telemetry_ms >= protocol.TELEMETRY_PERIOD_MS:
            self._last_telemetry_ms = now
            self._emit_telemetry(now)

    def _check_deadman(self, now: float) -> None:
        if now - self._last_command_ms <= protocol.DEADMAN_MS:
            return
        if self._deadman_tripped:
            return
        self._deadman_tripped = True
        self._motors = _MotorState()
        if self._fw_state != protocol.FW_STATE_STOPPED:
            self._fw_state = protocol.FW_STATE_ARMED

    def _advance_environment(self, now: float) -> None:
        # Slow random walks keep the dashboard visibly alive without ever
        # leaving the plausible ranges the telemetry validator enforces.
        self._temperature = _clamp(
            self._temperature + self._rng.uniform(-0.08, 0.08), 18.0, 46.0
        )
        self._humidity = _clamp(self._humidity + self._rng.uniform(-0.2, 0.2), 30.0, 85.0)
        self._gas = int(_clamp(self._gas + self._rng.uniform(-0.4, 0.4), 0, 18))

        # Range closes when driving forward and recovers otherwise, so a
        # close-range warning is reachable in a demo.
        if self._motors.direction == protocol.CMD_FORWARD and self._motors.speed > 0:
            self._range_cm = int(max(8, self._range_cm - self._motors.speed * 0.05))
        else:
            self._range_cm = int(min(400, self._range_cm + 2))

        if now >= self._next_motion_ms:
            self._motion_latch = 1
            self._next_motion_ms = now + self._rng.uniform(6000, 20000)

    def _emit_telemetry(self, now: float) -> None:
        values = {
            "temperature_c": self._temperature,
            "humidity_pct": self._humidity,
            "gas_ppm": self._gas,
            "motion": self._motion_latch,
            "range_cm": self._range_cm,
            "pan_angle": self._pan,
            "tilt_angle": self._tilt,
            "fw_state": self._fw_state,
            "uptime_ms": int(now - self._boot_ms),
        }
        line = protocol.format_telemetry_line(values)
        self._tx.extend((line + "\n").encode())
        self._motion_latch = 0

    # --- command pipeline (mirrors command_parser.cpp) ----------------------

    def _drain_commands(self) -> None:
        while b"\n" in self._rx:
            raw, _, rest = bytes(self._rx).partition(b"\n")
            self._rx = bytearray(rest)
            self._handle_line(raw.decode("ascii", errors="ignore").strip("\r"))

    def _handle_line(self, line: str) -> None:
        if not line:
            return

        # Stage 1: length.
        if len(line) > protocol.MAX_COMMAND_CHARS:
            self._respond("ERR_LEN")
            return

        opcode = line[0]

        # Stage 2: opcode whitelist.
        if opcode not in protocol.ALL_COMMANDS:
            self._respond("ERR_TOK")
            return

        # Stage 3: argument clamp.
        argument = 0
        tail = line[1:]
        if tail:
            if tail.isdigit():
                argument = int(tail)
                if argument > protocol.MAX_PWM:
                    argument = protocol.MAX_PWM
                    self._respond("WARN_CLAMP")
            else:
                argument = 0
                self._respond("WARN_CLAMP")

        now = _now_ms()

        if opcode in protocol.DEADMAN_ARMING_COMMANDS:
            self._arm(now)

        self._execute(opcode, argument, now)

    def _arm(self, now: float) -> None:
        self._last_command_ms = now
        self._deadman_tripped = False

    def _execute(self, opcode: str, argument: int, now: float) -> None:
        if opcode in {
            protocol.CMD_FORWARD,
            protocol.CMD_REVERSE,
            protocol.CMD_LEFT,
            protocol.CMD_RIGHT,
        }:
            self._motors = _MotorState(speed=argument, direction=opcode)
            self._fw_state = (
                protocol.FW_STATE_DRIVING if argument > 0 else protocol.FW_STATE_ARMED
            )
        elif opcode == protocol.CMD_STOP:
            self._motors = _MotorState()
            self._fw_state = protocol.FW_STATE_ARMED
        elif opcode == protocol.CMD_HEARTBEAT:
            pass
        elif opcode == protocol.CMD_PAN:
            self._pan = int(_clamp(argument, 0, protocol.SERVO_MAX_ANGLE))
        elif opcode == protocol.CMD_TILT:
            self._tilt = int(_clamp(argument, 0, protocol.SERVO_MAX_ANGLE))
        elif opcode == protocol.CMD_STATUS:
            self._emit_telemetry(now)

    def _respond(self, token: str) -> None:
        self._tx.extend((token + "\n").encode())


class MockSerial:
    """Minimal pyserial-compatible shim wrapping MockArduino."""

    def __init__(self, *_args, **_kwargs) -> None:
        self._board = MockArduino()
        self._buffer = bytearray()
        self.is_open = True
        self.dtr = True

    def write(self, data: bytes) -> int:
        return self._board.write(data)

    def readline(self) -> bytes:
        self._pump()
        if b"\n" in self._buffer:
            raw, _, rest = bytes(self._buffer).partition(b"\n")
            self._buffer = bytearray(rest)
            return raw + b"\n"
        return b""

    def _pump(self) -> None:
        self._buffer.extend(self._board.read_all())

    @property
    def in_waiting(self) -> int:
        self._pump()
        return len(self._buffer)

    def reset_input_buffer(self) -> None:
        self._buffer.clear()
        self._board.reset_buffers()

    def reset_output_buffer(self) -> None:
        pass

    def close(self) -> None:
        self.is_open = False

    def __enter__(self) -> "MockSerial":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


class MockGPS:
    """Emits NMEA sentences tracing a slow circular path near a fixed origin."""

    def __init__(self, *, lat: float = 23.8103, lon: float = 90.4125) -> None:
        self._origin = (lat, lon)
        self._angle = 0.0
        self._start = time.monotonic()

    def read_fix(self) -> dict[str, float | int | bool]:
        self._angle += 0.02
        radius = 0.0004  # roughly 45 metres
        lat = self._origin[0] + radius * math.sin(self._angle)
        lon = self._origin[1] + radius * math.cos(self._angle)
        # Report no fix for the first few seconds so the dashboard's
        # acquiring state is exercised.
        acquired = (time.monotonic() - self._start) > 3.0
        return {
            "lat": round(lat, 6) if acquired else None,
            "lon": round(lon, 6) if acquired else None,
            "gps_fix": acquired,
            "gps_sats": 9 if acquired else 0,
        }


def _now_ms() -> float:
    return time.monotonic() * 1000.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))
