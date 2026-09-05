/**
 * motors.cpp
 * -----------------------------------------------------------------------------
 * BTS7960 differential-drive implementation.
 *
 * Each side uses one BTS7960 with RPWM (forward) and LPWM (reverse) inputs.
 * A positive signed PWM drives RPWM; a negative value drives LPWM. Only one
 * of the two pins is ever active at a time to avoid shoot-through.
 * -----------------------------------------------------------------------------
 */

#include "motors.h"
#include "config.h"
#include "utils.h"

Motors g_motors;

Motors::Motors()
  : _dir(DIR_STOP),
    _targetSpeed(0),
    _leftCurrent(0),
    _rightCurrent(0),
    _leftTarget(0),
    _rightTarget(0),
    _enabled(false) {}

void Motors::init() {
  pinMode(LEFT_RPWM_PIN,  OUTPUT);
  pinMode(LEFT_LPWM_PIN,  OUTPUT);
  pinMode(RIGHT_RPWM_PIN, OUTPUT);
  pinMode(RIGHT_LPWM_PIN, OUTPUT);
  pinMode(MOTOR_EN_PIN,   OUTPUT);

  /* Boot safe: drivers disabled, all PWM zero. */
  analogWrite(LEFT_RPWM_PIN,  0);
  analogWrite(LEFT_LPWM_PIN,  0);
  analogWrite(RIGHT_RPWM_PIN, 0);
  analogWrite(RIGHT_LPWM_PIN, 0);

  digitalWrite(MOTOR_EN_PIN, LOW);
  _enabled      = false;
  _dir          = DIR_STOP;
  _targetSpeed  = 0;
  _leftCurrent  = _rightCurrent = 0;
  _leftTarget   = _rightTarget  = 0;
}

void Motors::enableDrivers(bool on) {
  _enabled = on;
  digitalWrite(MOTOR_EN_PIN, on ? HIGH : LOW);
  if (!on) {
    /* Force outputs low when disabling. */
    applyOutputs(0, 0);
    _leftCurrent = _rightCurrent = 0;
  }
}

void Motors::drive(MotorDirection dir, uint8_t speed) {
  _dir         = dir;
  _targetSpeed = speed;

  int s = (int)utils::clampInt(speed, MOTOR_PWM_MIN, MOTOR_PWM_MAX);

  switch (dir) {
    case DIR_FORWARD:
      _leftTarget  =  s;
      _rightTarget =  s;
      break;
    case DIR_REVERSE:
      _leftTarget  = -s;
      _rightTarget = -s;
      break;
    case DIR_LEFT:              /* pivot left: left back, right forward     */
      _leftTarget  = -s;
      _rightTarget =  s;
      break;
    case DIR_RIGHT:            /* pivot right: left forward, right back     */
      _leftTarget  =  s;
      _rightTarget = -s;
      break;
    case DIR_STOP:
    default:
      _leftTarget  = 0;
      _rightTarget = 0;
      break;
  }

  if (!_enabled && dir != DIR_STOP) {
    enableDrivers(true);
  }
}

void Motors::stop() {
  _dir         = DIR_STOP;
  _targetSpeed = 0;
  _leftTarget  = 0;
  _rightTarget = 0;
}

void Motors::emergencyStop() {
  _dir         = DIR_STOP;
  _targetSpeed = 0;
  _leftTarget  = _rightTarget  = 0;
  _leftCurrent = _rightCurrent = 0;
  applyOutputs(0, 0);
  enableDrivers(false);
}

int Motors::rampToward(int current, int target) {
  if (current < target) {
    current += MOTOR_RAMP_STEP;
    if (current > target) current = target;
  } else if (current > target) {
    current -= MOTOR_RAMP_STEP;
    if (current < target) current = target;
  }
  return current;
}

void Motors::service() {
  /* Ramp both channels toward their targets for smooth current draw. */
  _leftCurrent  = rampToward(_leftCurrent,  _leftTarget);
  _rightCurrent = rampToward(_rightCurrent, _rightTarget);

  if (_enabled) {
    applyOutputs(_leftCurrent, _rightCurrent);
  } else {
    applyOutputs(0, 0);
  }
}

void Motors::applyOutputs(int leftSigned, int rightSigned) {
  int lPwm = utils::clampInt(abs(leftSigned),  0, MOTOR_PWM_MAX);
  int rPwm = utils::clampInt(abs(rightSigned), 0, MOTOR_PWM_MAX);

  /* LEFT side: positive -> RPWM (forward), negative -> LPWM (reverse). */
  if (leftSigned >= 0) {
    analogWrite(LEFT_LPWM_PIN, 0);
    analogWrite(LEFT_RPWM_PIN, lPwm);
  } else {
    analogWrite(LEFT_RPWM_PIN, 0);
    analogWrite(LEFT_LPWM_PIN, lPwm);
  }

  /* RIGHT side. */
  if (rightSigned >= 0) {
    analogWrite(RIGHT_LPWM_PIN, 0);
    analogWrite(RIGHT_RPWM_PIN, rPwm);
  } else {
    analogWrite(RIGHT_RPWM_PIN, 0);
    analogWrite(RIGHT_LPWM_PIN, rPwm);
  }
}
