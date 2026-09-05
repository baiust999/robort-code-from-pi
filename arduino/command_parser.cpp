/**
 * command_parser.cpp
 * -----------------------------------------------------------------------------
 * Implementation of the non-blocking receiver and four-stage validation
 * pipeline. See command_parser.h for the stage descriptions.
 * -----------------------------------------------------------------------------
 */

#include "command_parser.h"
#include "config.h"
#include "protocol.h"
#include "robot_state.h"
#include "motors.h"
#include "servos.h"
#include "telemetry.h"
#include "utils.h"

CommandParser g_parser;

CommandParser::CommandParser() : _len(0), _overflow(false) {
  _buf[0] = '\0';
}

void CommandParser::init() {
  _len = 0;
  _overflow = false;
  _buf[0] = '\0';
}

/* -------------------------------------------------------------------------
 * Stage 1: Framing. Accumulate bytes until CMD_TERMINATOR.
 * ---------------------------------------------------------------------- */
void CommandParser::poll(unsigned long now) {
  while (Serial.available() > 0) {
    char c = (char)Serial.read();

    if (c == '\r') {
      continue;                     /* ignore CR                            */
    }

    if (c == CMD_TERMINATOR) {
      if (_overflow) {
        /* Frame was too long: discard and report. */
        g_telemetry.sendNack('?', CMD_ERR_EMPTY);
        _overflow = false;
        _len = 0;
        _buf[0] = '\0';
        continue;
      }
      _buf[_len] = '\0';
      if (_len > 0) {
        handleLine(_buf, now);
      }
      _len = 0;
      _buf[0] = '\0';
      continue;
    }

    if (_len < (RX_BUFFER_SIZE - 1)) {
      _buf[_len++] = c;
    } else {
      _overflow = true;             /* mark and keep draining to newline    */
    }
  }
}

/* -------------------------------------------------------------------------
 * Stages 2-4 orchestration + execution.
 * ---------------------------------------------------------------------- */
CmdResult CommandParser::handleLine(char *line, unsigned long now) {
  if (line == NULL || line[0] == '\0') {
    g_telemetry.sendNack('?', CMD_ERR_EMPTY);
    return CMD_ERR_EMPTY;
  }

  char opcode = line[0];
  const char *arg = &line[1];       /* remainder after opcode               */
  long value = 0;

  /* Stage 2 + 3: syntax and range. */
  CmdResult argCheck = validateArg(opcode, arg, &value);
  if (argCheck != CMD_OK) {
    g_telemetry.sendNack(opcode, argCheck);
    return argCheck;
  }

  /* Any well-formed command counts as comms activity for the dead-man
   * timer, even a query or heartbeat. */
  g_state.noteCommandReceived(now);

  /* Stage 4: state machine gate. */
  CmdResult stateCheck = checkState(opcode);
  if (stateCheck != CMD_OK) {
    g_telemetry.sendNack(opcode, stateCheck);
    return stateCheck;
  }

  execute(opcode, value, now);
  return CMD_OK;
}

CmdResult CommandParser::validateArg(char opcode, const char *arg,
                                     long *outValue) {
  *outValue = 0;

  switch (opcode) {
    /* Commands with a numeric speed argument (0-255). */
    case CMD_FORWARD:
    case CMD_REVERSE:
    case CMD_LEFT:
    case CMD_RIGHT: {
      if (arg[0] == '\0')            return CMD_ERR_ARG_MISSING;
      if (!utils::isAllDigits(arg))  return CMD_ERR_ARG_INVALID;
      long v = atol(arg);
      if (v < MOTOR_SPEED_MIN || v > MOTOR_SPEED_MAX) {
        return CMD_ERR_ARG_RANGE;
      }
      *outValue = v;
      return CMD_OK;
    }

    /* Servo commands with an angle argument (0-180). */
    case CMD_PAN:
    case CMD_TILT: {
      if (arg[0] == '\0')            return CMD_ERR_ARG_MISSING;
      if (!utils::isAllDigits(arg))  return CMD_ERR_ARG_INVALID;
      long v = atol(arg);
      if (v < SERVO_ANGLE_MIN || v > SERVO_ANGLE_MAX) {
        return CMD_ERR_ARG_RANGE;
      }
      *outValue = v;
      return CMD_OK;
    }

    /* Argument-less commands. Any trailing characters are ignored. */
    case CMD_STOP:
    case CMD_HEARTBEAT:
    case CMD_STATUS:
      return CMD_OK;

    default:
      return CMD_ERR_UNKNOWN;
  }
}

CmdResult CommandParser::checkState(char opcode) {
  /* Motion commands are gated by the state machine. */
  bool isMotion = (opcode == CMD_FORWARD || opcode == CMD_REVERSE ||
                   opcode == CMD_LEFT    || opcode == CMD_RIGHT);

  if (isMotion && !g_state.isMotionAllowed()) {
    return CMD_ERR_REJECTED;
  }

  /* Stop, heartbeat, status, and servo moves are always accepted; STOP
   * must remain available to recover from any state. */
  return CMD_OK;
}

void CommandParser::execute(char opcode, long value, unsigned long now) {
  (void)now;

  switch (opcode) {
    case CMD_FORWARD:
      g_state.setMode(MODE_ACTIVE);
      g_motors.drive(DIR_FORWARD, (uint8_t)value);
      g_telemetry.sendAck(opcode);
      break;

    case CMD_REVERSE:
      g_state.setMode(MODE_ACTIVE);
      g_motors.drive(DIR_REVERSE, (uint8_t)value);
      g_telemetry.sendAck(opcode);
      break;

    case CMD_LEFT:
      g_state.setMode(MODE_ACTIVE);
      g_motors.drive(DIR_LEFT, (uint8_t)value);
      g_telemetry.sendAck(opcode);
      break;

    case CMD_RIGHT:
      g_state.setMode(MODE_ACTIVE);
      g_motors.drive(DIR_RIGHT, (uint8_t)value);
      g_telemetry.sendAck(opcode);
      break;

    case CMD_STOP:
      g_motors.stop();
      /* Clear operator e-stop but leave hard faults (gas etc.) latched. */
      if (g_state.mode() == MODE_ESTOP) {
        g_state.clearFault();
      }
      if (g_state.mode() == MODE_ACTIVE) {
        g_state.setMode(MODE_READY);
      }
      g_telemetry.sendAck(opcode);
      break;

    case CMD_HEARTBEAT:
      /* Dead-man already refreshed in handleLine(). Acknowledge liveness. */
      g_telemetry.sendAck(opcode);
      break;

    case CMD_PAN:
      g_servos.setPan((uint8_t)value);
      g_telemetry.sendAck(opcode);
      break;

    case CMD_TILT:
      g_servos.setTilt((uint8_t)value);
      g_telemetry.sendAck(opcode);
      break;

    case CMD_STATUS:
      g_telemetry.sendStatus();
      break;

    default:
      g_telemetry.sendNack(opcode, CMD_ERR_UNKNOWN);
      break;
  }
}
