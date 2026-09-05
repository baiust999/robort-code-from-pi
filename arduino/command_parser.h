/**
 * command_parser.h
 * -----------------------------------------------------------------------------
 * Non-blocking UART command receiver and four-stage validation pipeline.
 *
 * Stage 1 (Framing)   : accumulate bytes until a newline terminator; reject
 *                       over-length frames.
 * Stage 2 (Syntax)    : opcode must be known; argument must be numeric when
 *                       required.
 * Stage 3 (Semantic)  : argument must fall within the command's legal range
 *                       (speed 0-255, angle 0-180).
 * Stage 4 (State)     : the robot state machine must permit the command
 *                       (e.g. motion is rejected while PANIC/ESTOP latched).
 *
 * Only after all four stages pass is the command executed.
 * -----------------------------------------------------------------------------
 */

#ifndef COMMAND_PARSER_H
#define COMMAND_PARSER_H

#include <Arduino.h>
#include "config.h"
#include "protocol.h"

class CommandParser {
 public:
  CommandParser();

  void init();

  /* Drain the UART RX buffer, framing complete lines and processing them.
   * Non-blocking: returns after consuming currently-available bytes. */
  void poll(unsigned long now);

 private:
  /* Run the full validation pipeline then execute. Returns the result. */
  CmdResult handleLine(char *line, unsigned long now);

  /* Stage 2+3 argument checks. Fills *outValue with the parsed argument. */
  CmdResult validateArg(char opcode, const char *arg, long *outValue);

  /* Stage 4: does the state machine permit this opcode right now? */
  CmdResult checkState(char opcode);

  /* Execute a fully-validated command. */
  void execute(char opcode, long value, unsigned long now);

  char    _buf[RX_BUFFER_SIZE];
  uint8_t _len;
  bool    _overflow;
};

extern CommandParser g_parser;

#endif /* COMMAND_PARSER_H */
