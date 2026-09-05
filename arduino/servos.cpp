/**
 * servos.cpp
 * -----------------------------------------------------------------------------
 * Pan / tilt servo implementation with angle clamping.
 * -----------------------------------------------------------------------------
 */

#include "servos.h"
#include "config.h"
#include "utils.h"

Servos g_servos;

Servos::Servos() : _pan(SERVO_PAN_HOME), _tilt(SERVO_TILT_HOME) {}

void Servos::init() {
  _panServo.attach(SERVO_PAN_PIN);
  _tiltServo.attach(SERVO_TILT_PIN);
  home();
}

void Servos::setPan(uint8_t angle) {
  _pan = (uint8_t)utils::clampInt(angle, SERVO_ANGLE_MIN, SERVO_ANGLE_MAX);
  _panServo.write(_pan);
}

void Servos::setTilt(uint8_t angle) {
  _tilt = (uint8_t)utils::clampInt(angle, SERVO_ANGLE_MIN, SERVO_ANGLE_MAX);
  _tiltServo.write(_tilt);
}

void Servos::home() {
  setPan(SERVO_PAN_HOME);
  setTilt(SERVO_TILT_HOME);
}
