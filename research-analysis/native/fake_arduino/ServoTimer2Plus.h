/**
 * Host-side stub of the ServoTimer2Plus library used by arduino/servos.h.
 * No real timer/PWM hardware exists on the test host; attach()/writeAngle()
 * are recorded no-ops so the real servos.cpp links and runs unmodified.
 * Angle clamping (0-180) happens in servos.cpp itself, not here.
 */
#ifndef FAKE_SERVO_TIMER2_PLUS_H
#define FAKE_SERVO_TIMER2_PLUS_H

class ServoTimer2Plus {
 public:
  void attach(int pin) { _pin = pin; }
  void writeAngle(int angle) { _lastAngle = angle; }
  int lastAngle() const { return _lastAngle; }

 private:
  int _pin = -1;
  int _lastAngle = -1;
};

#endif
