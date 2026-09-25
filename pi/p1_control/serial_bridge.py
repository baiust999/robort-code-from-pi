"""UART bridge to the Arduino, Sections 8.8.1.2 and 8.10.1.3.

Owns the only handle on the serial port. Performs the eight-step startup
handshake, then runs a reader loop that parses telemetry frames and a writer
path that serialises validated commands.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

from common import protocol
from common.config import P1Config
from common.logging_setup import EventLogger
from common.mock_hardware import MockSerial


class HandshakeError(RuntimeError):
    """Arduino did not reach READY within the handshake window."""


class SerialBridge:
    """Serial owner: handshake, telemetry ingest, command egress."""

    def __init__(self, config: P1Config, log: EventLogger) -> None:
        self._config = config
        self._log = log
        self._port: Any = None
        self._lock = asyncio.Lock()
        self._connected = False
        self._last_frame_ts = 0.0
        self._on_telemetry: Callable[[dict[str, Any]], None] | None = None
        self._on_event: Callable[[str], None] | None = None
        self._reader_task: asyncio.Task[None] | None = None

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def last_frame_age_ms(self) -> float:
        if not self._last_frame_ts:
            return float("inf")
        return (time.monotonic() - self._last_frame_ts) * 1000.0

    def set_handlers(
        self,
        on_telemetry: Callable[[dict[str, Any]], None],
        on_event: Callable[[str], None],
    ) -> None:
        self._on_telemetry = on_telemetry
        self._on_event = on_event

    # --- startup handshake, Section 8.8.1.2 --------------------------------

    async def open(self) -> None:
        """Steps 2-6 of the startup sequence. Raises HandshakeError on timeout."""
        self._port = self._open_port()

        # Opening the port toggles DTR, resetting the board into its safe boot.
        self._log.info("SERIAL_OPEN", "serial port opened", port=self._describe_port())
        await asyncio.sleep(protocol.ARDUINO_BOOT_WAIT_S)

        self._port.reset_input_buffer()
        self._port.reset_output_buffer()

        # Three STOPs before anything else: if the board survived a P1 crash
        # while driving, this halts it before we do anything slower.
        for _ in range(protocol.HANDSHAKE_STOP_REPEATS):
            self._write_line(protocol.encode_command(protocol.CMD_STOP))
            await asyncio.sleep(protocol.HANDSHAKE_STOP_INTERVAL_S)

        self._write_line(protocol.encode_command(protocol.CMD_STATUS))
        await self._await_ready()

        self._connected = True
        self._log.info("HANDSHAKE_OK", "arduino ready")

    def _open_port(self) -> Any:
        if self._config.mock_hardware:
            self._log.info("MOCK_HARDWARE", "using emulated arduino")
            return MockSerial()
        import serial  # imported lazily so dev hosts need no pyserial

        return serial.Serial(
            port=self._config.serial_port,
            baudrate=self._config.serial_baud,
            timeout=0.1,
            exclusive=True,  # O_EXCL: kernel rejects a second opener
        )

    def _describe_port(self) -> str:
        return "mock" if self._config.mock_hardware else self._config.serial_port

    async def _await_ready(self) -> None:
        deadline = time.monotonic() + protocol.HANDSHAKE_READY_TIMEOUT_S
        while time.monotonic() < deadline:
            line = self._read_line()
            if line is None:
                await asyncio.sleep(0.02)
                continue
            if line.startswith(protocol.READY_TOKEN):
                return
            # A telemetry frame answering the '?' query also proves the board
            # is alive and running our firmware.
            if protocol.parse_telemetry_line(line) is not None:
                return
        raise HandshakeError(
            f"no READY within {protocol.HANDSHAKE_READY_TIMEOUT_S}s"
        )

    # --- reader loop --------------------------------------------------------

    def start_reader(self) -> None:
        self._reader_task = asyncio.create_task(self._read_loop(), name="serial-reader")

    async def _read_loop(self) -> None:
        while True:
            try:
                drained = False
                while True:
                    line = self._read_line()
                    if line is None:
                        break
                    drained = True
                    self._dispatch(line)
                # Poll at a fraction of the 200ms frame period so a frame is
                # never delayed by more than a fifth of its cadence.
                await asyncio.sleep(0.005 if drained else 0.02)
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001 - loop must survive port faults
                self._connected = False
                self._log.exception("SERIAL_READ_FAIL", "serial read failed")
                await asyncio.sleep(0.5)

    def _dispatch(self, line: str) -> None:
        parsed = protocol.parse_telemetry_line(line)
        if parsed is not None:
            self._last_frame_ts = time.monotonic()
            self._connected = True
            if self._on_telemetry:
                self._on_telemetry(parsed)
            return

        # Everything else is a token: READY, PANIC, ALERT_OBSTACLE, ERR_*.
        self._log.info("DEBUG_RX", "arduino line", line=line)
        if self._on_event:
            self._on_event(line)
        if line.startswith(protocol.PANIC_TOKEN):
            self._log.critical("FW_PANIC", "firmware panic", detail=line)
        elif line.startswith(protocol.ALERT_OBSTACLE_TOKEN):
            self._log.warning("FW_OBSTACLE", "forward blocked by obstacle")
        elif line.startswith(("ERR_", "WARN_")):
            self._log.warning("FW_REJECT", "command rejected", token=line)

    # --- writer -------------------------------------------------------------

    async def send(self, opcode: str, argument: int | None = None) -> None:
        wire = protocol.encode_command(opcode, argument)
        self._log.info("DEBUG_TX", "sending to arduino", wire=wire.strip())
        async with self._lock:
            try:
                self._write_line(wire)
            except Exception:  # noqa: BLE001
                self._connected = False
                self._log.exception("SERIAL_WRITE_FAIL", "serial write failed")

    async def send_stop(self) -> None:
        await self.send(protocol.CMD_STOP)

    def _write_line(self, wire: str) -> None:
        if self._port is None:
            raise RuntimeError("serial port not open")
        self._port.write(wire.encode("ascii"))

    def _read_line(self) -> str | None:
        if self._port is None:
            return None
        raw = self._port.readline()
        if not raw:
            return None
        text = raw.decode("ascii", errors="ignore").strip()
        return text or None

    # --- shutdown -----------------------------------------------------------

    async def close(self) -> None:
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None

        if self._port is not None:
            try:
                self._write_line(protocol.encode_command(protocol.CMD_STOP))
                self._port.close()
            except Exception:  # noqa: BLE001 - best effort on the way out
                pass
            self._port = None
        self._connected = False
