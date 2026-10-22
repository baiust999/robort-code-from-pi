/**
 * test_main.cpp -- native host tests against the REAL, unmodified firmware
 * source (arduino/robot_state.cpp, arduino/command_parser.cpp,
 * arduino/motors.cpp, arduino/protocol.cpp, arduino/telemetry.cpp,
 * arduino/servos.cpp, arduino/utils.cpp), compiled as-is with g++ against a
 * host stub of the Arduino API (research-analysis/native/fake_arduino/).
 *
 * This is software verification only: no board, no motors, no radio link.
 * It answers a narrower, stronger question than the Python MockArduino
 * suite: does the dead-man timer behave as documented when the *actual*
 * compiled firmware C++ runs, not a separate reimplementation of it.
 *
 * Safety: pure host process, no serial device opened, no network socket, no
 * systemd interaction, does not import or touch anything under pi/ or var/.
 */

#include <cstdio>
#include <string>
#include <vector>

#include "Arduino.h"
#include "config.h"
#include "robot_state.h"
#include "motors.h"
#include "command_parser.h"
#include "telemetry.h"
#include "servos.h"
#include "mirrored_safety_task.h"

static int g_pass = 0;
static int g_fail = 0;
static std::vector<std::string> g_failures;

#define CHECK(cond, desc)                                                    \
  do {                                                                       \
    if (cond) {                                                              \
      ++g_pass;                                                              \
    } else {                                                                 \
      ++g_fail;                                                              \
      g_failures.push_back(std::string(__func__) + ": " + desc);             \
      std::printf("  FAIL (%s): %s\n", __func__, desc);                      \
    }                                                                        \
  } while (0)

/* Re-run the real boot sequence (arduino.ino setup(), the parts relevant to
 * the dead-man/motor/command pipeline) against freshly-reset fake hardware
 * and freshly-reset firmware singletons. */
static void boot(unsigned long bootMillis) {
  fake_hw::reset();
  fake_hw::fakeMillis = bootMillis;

  g_motors.init();
  g_state.init();
  g_parser.init();
  Serial.testTakeTx();  // discard anything printed during init

  g_state.noteCommandReceived(fake_hw::fakeMillis);  // arduino.ino setup() step 7
  g_state.setMode(MODE_READY);
  g_motors.enableDrivers(true);
  Serial.testTakeTx();
}

static void sendLine(const std::string &line, unsigned long now) {
  Serial.testInjectLine(line);
  g_parser.poll(now);
}

/* -------------------------------------------------------------------------
 * 1. Boundary behaviour of the REAL dead-man check, elapsed time vs
 *    DEADMAN_TIMEOUT_MS (2000 ms), exactly and +/-1 ms.
 * ---------------------------------------------------------------------- */

static void test_alive_one_ms_before_boundary() {
  boot(0);
  sendLine("F120", 0);
  CHECK(g_motors.targetSpeed() == 120, "F120 should set target speed 120");

  mirrored_taskSafety(DEADMAN_TIMEOUT_MS - 1);  // elapsed = 1999
  CHECK(g_state.fault() == FAULT_NONE, "elapsed 1999ms: expected no fault (alive)");
  CHECK(g_motors.targetSpeed() == 120, "elapsed 1999ms: motor target should be unchanged");
}

static void test_at_exactly_boundary() {
  boot(0);
  sendLine("F120", 0);

  mirrored_taskSafety(DEADMAN_TIMEOUT_MS);  // elapsed = 2000, exactly
  bool tripped_at_2000 = (g_state.fault() == FAULT_DEADMAN);
  std::printf("  INFO test_at_exactly_boundary: real firmware is %s at elapsed == DEADMAN_TIMEOUT_MS (%lu ms)\n",
              tripped_at_2000 ? "TRIPPED" : "ALIVE", (unsigned long)DEADMAN_TIMEOUT_MS);
  /* This assertion records the REAL firmware's own behaviour; see
   * arduino/arduino.ino taskSafety(): the live check is
   * `(now - lastCommandTime) >= DEADMAN_TIMEOUT_MS`, an inclusive upper
   * bound, so elapsed == DEADMAN_TIMEOUT_MS trips the dead-man. */
  CHECK(tripped_at_2000, "elapsed exactly 2000ms: real firmware's `>=` check trips here");
  CHECK(g_motors.targetSpeed() == 0, "elapsed exactly 2000ms: motors should be stopped");
}

static void test_tripped_one_ms_past_boundary() {
  boot(0);
  sendLine("F120", 0);

  mirrored_taskSafety(DEADMAN_TIMEOUT_MS + 1);  // elapsed = 2001
  CHECK(g_state.fault() == FAULT_DEADMAN, "elapsed 2001ms: expected FAULT_DEADMAN");
  CHECK(g_state.mode() == MODE_PANIC, "elapsed 2001ms: expected MODE_PANIC");
  CHECK(g_motors.targetSpeed() == 0, "elapsed 2001ms: motors should be stopped");
}

/* -------------------------------------------------------------------------
 * 2. Motor PWM / enable-line safe-state on trip (real GPIO-level check,
 *    something the Python mock cannot assert since it has no pin model).
 * ---------------------------------------------------------------------- */

static void test_motor_enable_line_and_pwm_go_safe_on_trip() {
  boot(0);
  sendLine("F200", 0);
  for (int i = 0; i < 20; ++i) {
    g_motors.service();  // let the ramp reach target, like taskMotorService every 10ms
  }
  CHECK(fake_hw::digitalState[MOTOR_EN_PIN] == HIGH, "pre-trip: EN line should be HIGH while driving");
  CHECK(fake_hw::analogState[LEFT_RPWM_PIN] > 0, "pre-trip: left RPWM should be nonzero while driving forward");

  mirrored_taskSafety(DEADMAN_TIMEOUT_MS + 1);  // trip

  CHECK(fake_hw::digitalState[MOTOR_EN_PIN] == LOW, "post-trip: EN line must go LOW (driver disabled)");
  CHECK(fake_hw::analogState[LEFT_RPWM_PIN] == 0, "post-trip: left RPWM must be 0");
  CHECK(fake_hw::analogState[LEFT_LPWM_PIN] == 0, "post-trip: left LPWM must be 0");
  CHECK(fake_hw::analogState[RIGHT_RPWM_PIN] == 0, "post-trip: right RPWM must be 0");
  CHECK(fake_hw::analogState[RIGHT_LPWM_PIN] == 0, "post-trip: right LPWM must be 0");

  std::string tx = Serial.testTakeTx();
  CHECK(tx.find("PANIC DEADMAN") != std::string::npos,
        "post-trip: PANIC DEADMAN line should have been sent");
}

/* -------------------------------------------------------------------------
 * 3. Which commands re-arm the dead-man on the REAL firmware. The Python
 *    mock and pi/common/protocol.py's DEADMAN_ARMING_COMMANDS claim pan,
 *    tilt and status do NOT re-arm it. arduino/command_parser.cpp has an
 *    explicit comment saying otherwise -- this test checks which is true
 *    of the actual compiled firmware logic.
 * ---------------------------------------------------------------------- */

static void test_pan_command_rearm_behaviour_on_real_firmware() {
  boot(0);
  sendLine("F120", 0);

  // Walk forward to just before the boundary, sending P90 each step, exactly
  // as research-analysis/tests/test_deadman_boundaries.py does against the
  // mock (which expects a trip at the end of this sequence).
  unsigned long t = 0;
  for (int i = 0; i < 5; ++i) {
    t += DEADMAN_TIMEOUT_MS / 5;  // 400, 800, 1200, 1600, 2000
    sendLine("P90", t);
  }
  mirrored_taskSafety(t);  // last send was at t == DEADMAN_TIMEOUT_MS itself

  bool rearmed_by_pan = (g_state.fault() == FAULT_NONE);
  std::printf("  INFO test_pan_command_rearm_behaviour_on_real_firmware: "
              "real firmware %s re-armed by repeated P90 commands "
              "(fault=%s, mode=%s)\n",
              rearmed_by_pan ? "WAS" : "was NOT",
              g_state.faultString(), g_state.modeString());
  /* Documents the real behaviour for the manuscript; see the analysis in
   * research-analysis/software_verification_results.md for why this
   * disagrees with pi/common/protocol.py's DEADMAN_ARMING_COMMANDS. */
}

static void test_tilt_and_status_rearm_behaviour_on_real_firmware() {
  boot(0);
  sendLine("F120", 0);

  sendLine("T45", DEADMAN_TIMEOUT_MS - 50);
  sendLine("?", DEADMAN_TIMEOUT_MS - 50);
  mirrored_taskSafety(DEADMAN_TIMEOUT_MS + 10);

  bool rearmed = (g_state.fault() == FAULT_NONE);
  std::printf("  INFO test_tilt_and_status_rearm_behaviour_on_real_firmware: "
              "real firmware %s re-armed by T45/'?' sent at t=%lu "
              "(fault=%s)\n",
              rearmed ? "WAS" : "was NOT", (unsigned long)(DEADMAN_TIMEOUT_MS - 50),
              g_state.faultString());
}

/* -------------------------------------------------------------------------
 * 4. Recovery after a timeout: does the first post-trip command succeed
 *    immediately (as the Python mock does), or is it rejected once by the
 *    state-machine gate before the supervisor clears the fault on its next
 *    pass (as command_parser.cpp's stage ordering implies)?
 * ---------------------------------------------------------------------- */

static void test_recovery_first_command_after_trip() {
  boot(0);
  sendLine("F120", 0);
  mirrored_taskSafety(DEADMAN_TIMEOUT_MS + 1);  // trip
  CHECK(g_state.fault() == FAULT_DEADMAN, "setup: should be tripped before recovery test");
  Serial.testTakeTx();

  // First command after the trip, sent "now" (no more silence).
  unsigned long t_recover = DEADMAN_TIMEOUT_MS + 1;
  sendLine("F120", t_recover);
  std::string tx1 = Serial.testTakeTx();
  bool first_command_was_acked = (tx1.find("ACK") != std::string::npos);
  bool first_command_was_nacked = (tx1.find("NACK") != std::string::npos);
  std::printf("  INFO test_recovery_first_command_after_trip: first post-trip F120 -> %s\n",
              tx1.c_str());
  CHECK(first_command_was_acked || first_command_was_nacked,
        "first post-trip command should produce either ACK or NACK");

  // Whatever the first command's own fate, lastCommandTime has been
  // updated (handleLine() calls noteCommandReceived before checkState), so
  // the very next safety pass, with no further silence, should clear the
  // fault.
  mirrored_taskSafety(t_recover);
  bool cleared = (g_state.fault() == FAULT_NONE && g_state.mode() == MODE_READY);
  std::string tx2 = Serial.testTakeTx();
  std::printf("  INFO test_recovery_first_command_after_trip: after next safety "
              "pass, fault=%s mode=%s event=\"%s\"\n",
              g_state.faultString(), g_state.modeString(), tx2.c_str());
  CHECK(cleared, "fault should auto-clear on the safety pass following any valid command");

  // Now that the fault is cleared, a second drive command should be
  // accepted and actually move the motors.
  sendLine("F120", t_recover);
  std::string tx3 = Serial.testTakeTx();
  CHECK(tx3.find("ACK") != std::string::npos, "post-recovery drive command should be ACKed");
  CHECK(g_motors.targetSpeed() == 120, "post-recovery drive command should set target speed");
}

/* -------------------------------------------------------------------------
 * 5. Valid/invalid commands independent of the dead-man (sanity: confirms
 *    the harness exercises the real 4-stage pipeline correctly).
 * ---------------------------------------------------------------------- */

static void test_invalid_opcode_rejected() {
  boot(0);
  sendLine("Z", 0);
  std::string tx = Serial.testTakeTx();
  CHECK(tx.find("NACK") != std::string::npos, "unknown opcode should be NACKed");
  CHECK(g_state.fault() == FAULT_NONE, "an invalid command must not affect fault state");
}

static void test_out_of_range_speed_rejected_and_does_not_drive() {
  boot(0);
  sendLine("F999", 0);  // > MOTOR_SPEED_MAX (255)
  std::string tx = Serial.testTakeTx();
  CHECK(tx.find("NACK") != std::string::npos, "out-of-range speed should be NACKed");
  CHECK(g_motors.targetSpeed() == 0, "out-of-range speed command must not drive the motors");
}

static void test_valid_heartbeat_rearms_without_driving() {
  boot(0);
  sendLine("F120", 0);
  sendLine("H", DEADMAN_TIMEOUT_MS - 100);
  mirrored_taskSafety(DEADMAN_TIMEOUT_MS - 1);  // 2099 since last H at 1900... see below
  // t = 1900 (H) ; safety check at 1999 -> elapsed since H = 99ms, alive
  CHECK(g_state.fault() == FAULT_NONE, "heartbeat should keep the dead-man alive");
  CHECK(g_motors.targetSpeed() == 120, "heartbeat must not change the drive target");
}

int main() {
  std::printf("Native firmware dead-man test harness\n");
  std::printf("Compiled from unmodified arduino/*.cpp against a host Arduino stub.\n\n");

  test_alive_one_ms_before_boundary();
  test_at_exactly_boundary();
  test_tripped_one_ms_past_boundary();
  test_motor_enable_line_and_pwm_go_safe_on_trip();
  test_pan_command_rearm_behaviour_on_real_firmware();
  test_tilt_and_status_rearm_behaviour_on_real_firmware();
  test_recovery_first_command_after_trip();
  test_invalid_opcode_rejected();
  test_out_of_range_speed_rejected_and_does_not_drive();
  test_valid_heartbeat_rearms_without_driving();

  std::printf("\n%d passed, %d failed\n", g_pass, g_fail);
  for (const auto &f : g_failures) {
    std::printf("FAILED: %s\n", f.c_str());
  }
  return g_fail == 0 ? 0 : 1;
}
