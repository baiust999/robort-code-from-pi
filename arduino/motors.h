/**
 * motors.h
 * -----------------------------------------------------------------------------
 * Differential-drive motor control for two BTS7960 dual half-bridge drivers
 * (one per side). Provides directional commands with PWM speed control, a
 * non-blocking speed ramp, and hardware fail-safe shutdown.
 * -----------------------------------------------------------------------------
 */

#ifndef MOTORS_H
#define MOTORS_H

#include <Arduino.h>

/* Direction of travel requested by the command layer. */
enum MotorDirection {
  DIR_STOP = 0,
  DIR_FORWARD,
  DIR_REVERSE,
  DIR_LEFT,
  DIR_RIGHT
};

class Motors {
 public:
  Motors();

  /* Configure pins, disable drivers, zero PWM. Safe to call at boot. */
  void init();

  /* Request a direction at the given speed (0-255). The actual PWM is
   * ramped toward the target by service(). */
  void drive(MotorDirection dir, uint8_t speed);

  /* Immediately cut all PWM and disable the drivers. Used for e-stop /
   * panic / dead-man. Bypasses ramping. */
  void emergencyStop();

  /* Normal stop (ramps down to zero). */
  void stop();

  /* Non-blocking service: advances the PWM ramp toward the target. Must be
   * called periodically from the scheduler. */
  void service();

  /* Re-enable the drivers after a fault has been cleared. */
  void enableDrivers(bool on);

  MotorDirection direction() const { return _dir; }
  uint8_t        targetSpeed() const { return _targetSpeed; }

 private:
  void applyOutputs(int leftSigned, int rightSigned);
  int  rampToward(int current, int target);

  MotorDirection _dir;
  uint8_t        _targetSpeed;   /* requested speed 0-255                    */
  int            _leftCurrent;   /* current signed PWM (-255..255)           */
  int            _rightCurrent;
  int            _leftTarget;    /* target signed PWM                        */
  int            _rightTarget;
  bool           _enabled;
};

extern Motors g_motors;

#endif /* MOTORS_H */
