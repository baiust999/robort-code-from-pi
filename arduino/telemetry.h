/**
 * telemetry.h
 * -----------------------------------------------------------------------------
 * Formats and transmits all outbound UART messages: READY banner, ACK/NACK
 * responses, periodic telemetry, heartbeat, status reports and PANIC alerts.
 * -----------------------------------------------------------------------------
 */

#ifndef TELEMETRY_H
#define TELEMETRY_H

#include <Arduino.h>
#include "protocol.h"

/* Declared in protocol.cpp. */
const char* cmdResultString(CmdResult r);

class Telemetry {
 public:
  Telemetry();

  /* Emit the boot banner: "READY <fw> <ver>". */
  void sendReady();

  /* Acknowledge a successfully executed command. */
  void sendAck(char opcode);

  /* Report a rejected/invalid command with a reason. */
  void sendNack(char opcode, CmdResult reason);

  /* Periodic full telemetry line (sensors + state). */
  void sendTelemetry();

  /* Compact heartbeat line. */
  void sendHeartbeat();

  /* Full status snapshot in response to '?'. */
  void sendStatus();

  /* Emergency PANIC alert with the active fault reason. */
  void sendPanic();

  /* Generic event notification (e.g. obstacle auto-stop). */
  void sendEvent(const char *text);
};

extern Telemetry g_telemetry;

#endif /* TELEMETRY_H */
