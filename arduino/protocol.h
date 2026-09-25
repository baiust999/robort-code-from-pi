/**
 * protocol.h
 * -----------------------------------------------------------------------------
 * UART wire-protocol definitions shared by the parser and telemetry modules.
 *
 * Inbound command grammar (ASCII, newline terminated):
 *   F<speed>   forward      speed 0-255
 *   R<speed>   reverse      speed 0-255
 *   L<speed>   turn left    speed 0-255
 *   G<speed>   turn right   speed 0-255   (G = "go right")
 *   S          stop
 *   H          heartbeat / keep-alive
 *   P<angle>   pan servo    angle 0-180
 *   T<angle>   tilt servo   angle 0-180
 *   ?          status query
 *
 * Outbound messages are line-based ASCII strings prefixed by a type tag
 * (see the TAG_* constants) so the host parser can dispatch easily.
 * -----------------------------------------------------------------------------
 */

#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <Arduino.h>

/* Command opcodes (first byte of an inbound command). */
#define CMD_FORWARD    'F'
#define CMD_REVERSE    'R'
#define CMD_LEFT       'L'
#define CMD_RIGHT      'G'
#define CMD_STOP       'S'
#define CMD_HEARTBEAT  'H'
#define CMD_PAN        'P'
#define CMD_TILT       'T'
#define CMD_STATUS     '?'

/* Outbound line tags. */
#define TAG_READY      "READY"
#define TAG_STATUS     "STATUS"
#define TAG_HEARTBEAT  "HB"
#define TAG_ACK        "ACK"
#define TAG_NACK       "NACK"
#define TAG_PANIC      "PANIC"
#define TAG_EVENT      "EVT"

/* Periodic telemetry frame, Section 8.7.5. Untagged CSV, positional fields:
 *   temperature_c,humidity_pct,gas_ppm,motion,range_cm,
 *   pan_angle,tilt_angle,fw_state,uptime_ms
 * Order and field count are load-bearing: parsed positionally by
 * pi/common/protocol.py:parse_telemetry_line / TELEMETRY_FIELDS. */

/* Firmware state values for the fw_state field. Mirrors FW_STATE_* in
 * pi/common/protocol.py. */
#define FW_STATE_ARMED    1
#define FW_STATE_DRIVING  2
#define FW_STATE_STOPPED  3

/* Result codes from command validation / execution. */
enum CmdResult {
  CMD_OK = 0,
  CMD_ERR_EMPTY,        /* no data                                        */
  CMD_ERR_UNKNOWN,      /* unrecognised opcode                            */
  CMD_ERR_ARG_MISSING,  /* opcode requires an argument but none given     */
  CMD_ERR_ARG_INVALID,  /* argument not numeric                           */
  CMD_ERR_ARG_RANGE,    /* argument out of allowed range                  */
  CMD_ERR_REJECTED      /* rejected by state machine (e.g. panic latched) */
};

#endif /* PROTOCOL_H */
