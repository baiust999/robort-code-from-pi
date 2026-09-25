/**
 * sensors.h
 * -----------------------------------------------------------------------------
 * Sensor acquisition layer. Aggregates all onboard sensors and writes results
 * into the shared SensorData snapshot in RobotState.
 *
 * Sensors:
 *   - HC-SR04  ultrasonic distance   (fast poll, non-blocking pulseIn)
 *   - HC-SR501 PIR motion            (interrupt driven, INT0)
 *   - DHT11    temperature/humidity  (slow poll)
 *   - MQ-136   gas                   (slow poll, analog)
 * -----------------------------------------------------------------------------
 */

#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

class Sensors {
 public:
  Sensors();

  /* Configure sensor pins and attach the PIR interrupt. */
  void init();

  /* Fast sensor group: ultrasonic + IR. Call from the fast scheduler task. */
  void serviceFast();

  /* Slow sensor group: DHT11 + gas. Call from the slow scheduler task. */
  void serviceSlow();

  /* ISR entry point for the PIR motion sensor (called from a free function). */
  static void onMotionISR();

 private:
  uint16_t readUltrasonicCm();
  void     readDHT();
  void     readGas();

  /* DHT11 low-level single-wire read. Returns true on success and fills
   * temperature (deg C) and humidity (%). */
  bool     dhtRead(int8_t *tempC, uint8_t *humidity);
};

extern Sensors g_sensors;

/* Volatile flag set by the PIR ISR, consumed in serviceFast(). */
extern volatile bool g_motionFlag;

#endif /* SENSORS_H */
