/**
 * servos.h
 * -----------------------------------------------------------------------------
 * Pan / tilt camera gimbal control using the Arduino Servo library. Enforces
 * 0-180 degree limits and centres both servos at boot.
 * -----------------------------------------------------------------------------
 */

#ifndef SERVOS_H
#define SERVOS_H

#include <Arduino.h>
#include <Servo.h>

class Servos {
 public:
  Servos();

  /* Attach servos and move them to their home (centre) positions. */
  void init();

  /* Set pan angle (0-180). Value is clamped to the valid range. */
  void setPan(uint8_t angle);

  /* Set tilt angle (0-180). Value is clamped to the valid range. */
  void setTilt(uint8_t angle);

  /* Return to home positions. */
  void home();

  uint8_t pan() const  { return _pan; }
  uint8_t tilt() const { return _tilt; }

 private:
  Servo   _panServo;
  Servo   _tiltServo;
  uint8_t _pan;
  uint8_t _tilt;
};

extern Servos g_servos;

#endif /* SERVOS_H */
