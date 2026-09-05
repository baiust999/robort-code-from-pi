/**
 * protocol.cpp
 * -----------------------------------------------------------------------------
 * Helper to translate CmdResult codes into human-readable strings for NACK
 * responses. Kept separate so both the parser and telemetry layers can use it.
 * -----------------------------------------------------------------------------
 */

#include "protocol.h"

const char* cmdResultString(CmdResult r) {
  switch (r) {
    case CMD_OK:               return "OK";
    case CMD_ERR_EMPTY:        return "EMPTY";
    case CMD_ERR_UNKNOWN:      return "UNKNOWN_CMD";
    case CMD_ERR_ARG_MISSING:  return "ARG_MISSING";
    case CMD_ERR_ARG_INVALID:  return "ARG_INVALID";
    case CMD_ERR_ARG_RANGE:    return "ARG_RANGE";
    case CMD_ERR_REJECTED:     return "REJECTED";
    default:                   return "ERR";
  }
}
