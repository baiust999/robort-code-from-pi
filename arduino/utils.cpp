/**
 * utils.cpp
 * -----------------------------------------------------------------------------
 * Implementation of shared helper routines. See utils.h for contracts.
 * -----------------------------------------------------------------------------
 */

#include "utils.h"

namespace utils {

int clampInt(int value, int lo, int hi) {
  if (value < lo) return lo;
  if (value > hi) return hi;
  return value;
}

long clampLong(long value, long lo, long hi) {
  if (value < lo) return lo;
  if (value > hi) return hi;
  return value;
}

bool elapsed(unsigned long now, unsigned long *last, unsigned long period) {
  /* Unsigned subtraction handles millis() rollover correctly. */
  if ((unsigned long)(now - *last) >= period) {
    *last = now;
    return true;
  }
  return false;
}

bool isAllDigits(const char *s) {
  if (s == NULL || *s == '\0') {
    return false;
  }
  for (const char *p = s; *p != '\0'; ++p) {
    if (*p < '0' || *p > '9') {
      return false;
    }
  }
  return true;
}

} /* namespace utils */
