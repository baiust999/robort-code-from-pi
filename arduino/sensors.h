/**
 * sensors.h
 * -----------------------------------------------------------------------------
 * Sensor acquisition layer. Aggregates all onboard sensors and writes results
 * into the shared SensorData snapshot in RobotState.
 *
 * Sensors:
 *   - HC-SR04  ultrasonic distance   (fast poll, non-blocking pulseIn)
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

  /* Configure sensor pins. */
  void init();

  /* Fast sensor group: ultrasonic. Call from the fast scheduler task. */
  void serviceFast();

  /* Slow sensor group: DHT11 + gas. Call from the slow scheduler task. */
  void serviceSlow();

 private:
  uint16_t readUltrasonicCm();
  void     readDHT();
  void     readGas();

  /* DHT11 low-level single-wire read. Returns true on success and fills
   * temperature (deg C) and humidity (%). */
  bool     dhtRead(int8_t *tempC, uint8_t *humidity);
};

extern Sensors g_sensors;

#endif /* SENSORS_H */
