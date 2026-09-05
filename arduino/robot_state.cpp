/**
 * robot_state.cpp
 * -----------------------------------------------------------------------------
 * Implementation of the robot finite-state machine and shared state store.
 * -----------------------------------------------------------------------------
 */

#include "robot_state.h"
#include "config.h"

/* Global singleton. */
RobotState g_state;

RobotState::RobotState()
  : _mode(MODE_BOOT),
    _fault(FAULT_NONE),
    _lastCmdTime(0) {
  _sensors.distanceCm   = ULTRASONIC_MAX_CM;
  _sensors.irLeft       = false;
  _sensors.irRight      = false;
  _sensors.motion       = false;
  _sensors.temperatureC = 0;
  _sensors.humidity     = 0;
  _sensors.gasRaw       = 0;
  _sensors.gasAlarm     = false;
  _sensors.dhtValid     = false;
}

void RobotState::init() {
  _mode        = MODE_BOOT;
  _fault       = FAULT_NONE;
  _lastCmdTime = millis();
}

void RobotState::setMode(RobotMode m) {
  _mode = m;
}

bool RobotState::isMotionAllowed() const {
  /* Motion is only permitted while READY or ACTIVE and no fault latched. */
  return (_mode == MODE_READY || _mode == MODE_ACTIVE) &&
         (_fault == FAULT_NONE);
}

void RobotState::setFault(FaultReason r) {
  _fault = r;
  if (r == FAULT_OPERATOR_ESTOP) {
    _mode = MODE_ESTOP;
  } else if (r != FAULT_NONE) {
    _mode = MODE_PANIC;
  }
}

void RobotState::clearFault() {
  _fault = FAULT_NONE;
  if (_mode == MODE_PANIC || _mode == MODE_ESTOP) {
    _mode = MODE_READY;
  }
}

void RobotState::noteCommandReceived(unsigned long now) {
  _lastCmdTime = now;
}

const char* RobotState::modeString() const {
  switch (_mode) {
    case MODE_BOOT:   return "BOOT";
    case MODE_READY:  return "READY";
    case MODE_ACTIVE: return "ACTIVE";
    case MODE_ESTOP:  return "ESTOP";
    case MODE_PANIC:  return "PANIC";
    default:          return "UNKNOWN";
  }
}

const char* RobotState::faultString() const {
  switch (_fault) {
    case FAULT_NONE:           return "NONE";
    case FAULT_DEADMAN:        return "DEADMAN";
    case FAULT_GAS:            return "GAS";
    case FAULT_OBSTACLE:       return "OBSTACLE";
    case FAULT_OPERATOR_ESTOP: return "ESTOP";
    default:                   return "UNKNOWN";
  }
}
