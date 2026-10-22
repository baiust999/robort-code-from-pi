/**
 * mirrored_safety_task.h
 * -----------------------------------------------------------------------------
 * NOT production code. arduino/arduino.ino's taskSafety() is a static free
 * function private to that .ino translation unit, so a separate test binary
 * cannot link against it directly. This header is a byte-for-byte copy of its
 * body (arduino/arduino.ino, lines 75-97 as of this writing) so the test
 * harness can drive the real dead-man decision exactly as the firmware does,
 * calling only the real, unmodified g_state/g_motors/g_telemetry objects
 * compiled from arduino/robot_state.cpp, arduino/motors.cpp and
 * arduino/telemetry.cpp.
 *
 * If arduino/arduino.ino's taskSafety() ever changes, this copy must be
 * updated to match or the native tests stop being evidence about the real
 * firmware. This is the one piece of firmware control flow not compiled
 * directly from arduino/ in this harness, and is called out as such in
 * research-analysis/software_verification_results.md.
 * -----------------------------------------------------------------------------
 */
#ifndef MIRRORED_SAFETY_TASK_H
#define MIRRORED_SAFETY_TASK_H

#include "robot_state.h"
#include "motors.h"
#include "telemetry.h"
#include "config.h"

inline void mirrored_taskSafety(unsigned long now) {
  if ((unsigned long)(now - g_state.lastCommandTime()) >= DEADMAN_TIMEOUT_MS) {
    if (g_state.fault() != FAULT_DEADMAN &&
        g_state.mode()  != MODE_PANIC    &&
        g_state.mode()  != MODE_ESTOP) {
      g_state.setFault(FAULT_DEADMAN);
      g_motors.emergencyStop();
      g_telemetry.sendPanic();
    }
    return;
  }

  if (g_state.fault() == FAULT_DEADMAN &&
      (unsigned long)(now - g_state.lastCommandTime()) < DEADMAN_TIMEOUT_MS) {
    g_state.clearFault();
    g_motors.enableDrivers(true);
    g_telemetry.sendEvent("DEADMAN_CLEARED");
  }
}

#endif
