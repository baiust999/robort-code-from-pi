/**
 * telemetry.cpp
 * -----------------------------------------------------------------------------
 * Outbound message formatting. Uses direct Serial.print calls (no dynamic
 * String allocation) to keep RAM usage predictable on the UNO.
 *
 * Telemetry line format (semicolon-delimited key=value pairs):
 *   TELEM;MODE=<m>;FAULT=<f>;DIR=<d>;SPD=<n>;DIST=<cm>;IRL=<0|1>;IRR=<0|1>;
 *         MOT=<0|1>;T=<c>;H=<%>;GAS=<raw>;GALM=<0|1>;PAN=<a>;TILT=<a>
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

void Telemetry::sendTelemetry() {
  const SensorData &s = g_state.sensors();

  Serial.print(TAG_TELEMETRY);
  Serial.print(";MODE=");  Serial.print(g_state.modeString());
  Serial.print(";FAULT="); Serial.print(g_state.faultString());
  Serial.print(";DIR=");   Serial.print(directionString(g_motors.direction()));
  Serial.print(";SPD=");   Serial.print(g_motors.targetSpeed());
  Serial.print(";DIST=");  Serial.print(s.distanceCm);
  Serial.print(";IRL=");   Serial.print(s.irLeft ? 1 : 0);
  Serial.print(";IRR=");   Serial.print(s.irRight ? 1 : 0);
  Serial.print(";MOT=");   Serial.print(s.motion ? 1 : 0);
  Serial.print(";T=");     Serial.print(s.dhtValid ? (int)s.temperatureC : -99);
  Serial.print(";H=");     Serial.print(s.dhtValid ? (int)s.humidity : 0);
  Serial.print(";GAS=");   Serial.print(s.gasRaw);
  Serial.print(";GALM=");  Serial.print(s.gasAlarm ? 1 : 0);
  Serial.print(";PAN=");   Serial.print(g_servos.pan());
  Serial.print(";TILT=");  Serial.println(g_servos.tilt());
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
  Serial.print(";IRL=");   Serial.print(s.irLeft ? 1 : 0);
  Serial.print(";IRR=");   Serial.print(s.irRight ? 1 : 0);
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
