/**
 * telemetry.cpp
 * -----------------------------------------------------------------------------
 * Outbound message formatting. Uses direct Serial.print calls (no dynamic
 * String allocation) to keep RAM usage predictable on the UNO.
 *
 * Telemetry line format: untagged CSV, positional fields (Section 8.7.5),
 * parsed by pi/common/protocol.py:parse_telemetry_line:
 *   temperature_c,humidity_pct,gas_ppm,motion,range_cm,
 *   pan_angle,tilt_angle,fw_state,uptime_ms
 * -----------------------------------------------------------------------------
 */

#include "telemetry.h"
#include "config.h"
#include "robot_state.h"
#include "motors.h"
#include "servos.h"

Telemetry g_telemetry;

Telemetry::Telemetry() {}

static const char* directionString(MotorDirection d) {
  switch (d) {
    case DIR_FORWARD: return "F";
    case DIR_REVERSE: return "R";
    case DIR_LEFT:    return "L";
    case DIR_RIGHT:   return "G";
    case DIR_STOP:
    default:          return "S";
  }
}

void Telemetry::sendReady() {
  Serial.print(TAG_READY);
  Serial.print(' ');
  Serial.print(FW_NAME);
  Serial.print(' ');
  Serial.println(FW_VERSION);
}

void Telemetry::sendAck(char opcode) {
  Serial.print(TAG_ACK);
  Serial.print(' ');
  Serial.println(opcode);
}

void Telemetry::sendNack(char opcode, CmdResult reason) {
  Serial.print(TAG_NACK);
  Serial.print(' ');
  Serial.print(opcode);
  Serial.print(' ');
  Serial.println(cmdResultString(reason));
}

/* Maps the firmware mode to the fw_state value the Pi parser expects
 * (range 1-3). BOOT, ESTOP and PANIC all report STOPPED since none of them
 * permit motion. */
static uint8_t telemetryFwState() {
  switch (g_state.mode()) {
    case MODE_ACTIVE: return FW_STATE_DRIVING;
    case MODE_READY:  return FW_STATE_ARMED;
    default:          return FW_STATE_STOPPED;
  }
}

void Telemetry::sendTelemetry() {
  const SensorData &s = g_state.sensors();

  /* Untagged CSV; last known temperature/humidity (dhtValid or not) are
   * always in-range for the Pi parser, unlike a sentinel such as -99. */
  Serial.print((int)s.temperatureC);   Serial.print(',');
  Serial.print(s.humidity);            Serial.print(',');
  Serial.print(s.gasRaw);              Serial.print(',');
  Serial.print(s.motion ? 1 : 0);      Serial.print(',');
  Serial.print(s.distanceCm);          Serial.print(',');
  Serial.print(g_servos.pan());        Serial.print(',');
  Serial.print(g_servos.tilt());       Serial.print(',');
  Serial.print(telemetryFwState());    Serial.print(',');
  Serial.println(millis());
}

void Telemetry::sendHeartbeat() {
  Serial.print(TAG_HEARTBEAT);
  Serial.print(' ');
  Serial.print(g_state.modeString());
  Serial.print(' ');
  Serial.println(millis());
}

void Telemetry::sendStatus() {
  const SensorData &s = g_state.sensors();

  Serial.print(TAG_STATUS);
  Serial.print(";FW=");    Serial.print(FW_NAME);
  Serial.print(";VER=");   Serial.print(FW_VERSION);
  Serial.print(";MODE=");  Serial.print(g_state.modeString());
  Serial.print(";FAULT="); Serial.print(g_state.faultString());
  Serial.print(";UPTIME=");Serial.print(millis());
  Serial.print(";DIR=");   Serial.print(directionString(g_motors.direction()));
  Serial.print(";SPD=");   Serial.print(g_motors.targetSpeed());
  Serial.print(";DIST=");  Serial.print(s.distanceCm);
  Serial.print(";MOT=");   Serial.print(s.motion ? 1 : 0);
  Serial.print(";T=");     Serial.print(s.dhtValid ? (int)s.temperatureC : -99);
  Serial.print(";H=");     Serial.print(s.dhtValid ? (int)s.humidity : 0);
  Serial.print(";GAS=");   Serial.print(s.gasRaw);
  Serial.print(";GALM=");  Serial.print(s.gasAlarm ? 1 : 0);
  Serial.print(";PAN=");   Serial.print(g_servos.pan());
  Serial.print(";TILT=");  Serial.println(g_servos.tilt());
}

void Telemetry::sendPanic() {
  Serial.print(TAG_PANIC);
  Serial.print(' ');
  Serial.println(g_state.faultString());
}

void Telemetry::sendEvent(const char *text) {
  Serial.print(TAG_EVENT);
  Serial.print(' ');
  Serial.println(text);
}
