/**
 * utils.h
 * -----------------------------------------------------------------------------
 * Small stateless helper routines shared across modules: clamping, mapping,
 * elapsed-time helpers and a lightweight debug print macro.
 * -----------------------------------------------------------------------------
 */

#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include "config.h"

/* Debug print helper. Compiles to nothing when DEBUG_ENABLED == 0. */
#if DEBUG_ENABLED
  #define DBG_PRINT(x)    Serial.print(x)
  #define DBG_PRINTLN(x)  Serial.println(x)
#else
  #define DBG_PRINT(x)
  #define DBG_PRINTLN(x)
#endif

namespace utils {

/* Clamp an integer to [lo, hi]. */
int   clampInt(int value, int lo, int hi);

/* Clamp a long to [lo, hi]. */
long  clampLong(long value, long lo, long hi);

/* Non-blocking elapsed check. Returns true and advances *last by period
 * when (now - *last) >= period. Handles millis() overflow safely. */
bool  elapsed(unsigned long now, unsigned long *last, unsigned long period);

/* Returns true if a null-terminated string is composed solely of ASCII
 * decimal digits (and is non-empty). */
bool  isAllDigits(const char *s);

} /* namespace utils */

#endif /* UTILS_H */
