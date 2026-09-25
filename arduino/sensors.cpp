/**
 * sensors.cpp
 * -----------------------------------------------------------------------------
 * Sensor acquisition implementation. DHT11 is read with a self-contained
 * bit-banged single-wire routine so no third-party library is needed.
 * -----------------------------------------------------------------------------
 */

#include "sensors.h"
#include "config.h"
#include "robot_state.h"
#include "utils.h"

Sensors g_sensors;
volatile bool g_motionFlag = false;

/* Free-function ISR trampoline required by attachInterrupt(). */
static void motionInterruptTrampoline() {
  Sensors::onMotionISR();
}

Sensors::Sensors() {}

void Sensors::init() {
  pinMode(ULTRASONIC_TRIG_PIN, OUTPUT);
  pinMode(ULTRASONIC_ECHO_PIN, INPUT);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

  pinMode(IR_LEFT_PIN,  INPUT_PULLUP);
  pinMode(IR_RIGHT_PIN, INPUT_PULLUP);

  pinMode(PIR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIR_PIN),
                  motionInterruptTrampoline, RISING);

  pinMode(DHT_PIN, INPUT_PULLUP);
  /* GAS_PIN is analog, no pinMode needed. */
}

void Sensors::onMotionISR() {
  g_motionFlag = true;
}

/* ---------------------------------------------------------------------------
 * HC-SR04 ultrasonic distance measurement.
 * pulseIn is bounded by ULTRASONIC_TIMEOUT_US so the fast task stays snappy.
 * ------------------------------------------------------------------------- */
uint16_t Sensors::readUltrasonicCm() {
  /* 10 us trigger pulse. */
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG_PIN, LOW);

  unsigned long duration =
      pulseIn(ULTRASONIC_ECHO_PIN, HIGH, ULTRASONIC_TIMEOUT_US);

  if (duration == 0) {
    /* Timeout: treat as no obstacle within range. */
    return ULTRASONIC_MAX_CM;
  }

  /* Distance (cm) = duration_us / 58. */
  unsigned long cm = duration / 58UL;
  if (cm > ULTRASONIC_MAX_CM) {
    cm = ULTRASONIC_MAX_CM;
  }
  return (uint16_t)cm;
}

void Sensors::readIR() {
  SensorData &s = g_state.sensors();
  s.irLeft  = (digitalRead(IR_LEFT_PIN)  == IR_OBSTACLE_ACTIVE);
  s.irRight = (digitalRead(IR_RIGHT_PIN) == IR_OBSTACLE_ACTIVE);
}

void Sensors::readGas() {
  SensorData &s = g_state.sensors();
  s.gasRaw   = (uint16_t)analogRead(GAS_PIN);
  s.gasAlarm = (s.gasRaw >= GAS_ALARM_THRESHOLD);
}

void Sensors::serviceFast() {
  SensorData &s = g_state.sensors();

  s.distanceCm = readUltrasonicCm();
  readIR();

  /* Latch motion flag set by the ISR. */
  noInterrupts();
  bool motion = g_motionFlag;
  g_motionFlag = false;
  interrupts();
  if (motion) {
    s.motion = true;
  }
}

void Sensors::serviceSlow() {
  readDHT();
  readGas();
  /* Motion is a momentary event; clear it each slow cycle so telemetry
   * reflects recent activity rather than latching forever. */
  g_state.sensors().motion = false;
}

/* ---------------------------------------------------------------------------
 * DHT11 bit-banged single-wire read.
 * Protocol: MCU pulls line low >=18 ms, releases, then the sensor sends
 * 40 bits (humidity int, humidity dec, temp int, temp dec, checksum).
 * DHT11 decimals are always zero, so we use the integer bytes.
 * ------------------------------------------------------------------------- */
bool Sensors::dhtRead(int8_t *tempC, uint8_t *humidity) {
  uint8_t bytes[5] = {0, 0, 0, 0, 0};

  /* Start signal. */
  pinMode(DHT_PIN, OUTPUT);
  digitalWrite(DHT_PIN, LOW);
  delay(20);                       /* >=18 ms low                          */
  digitalWrite(DHT_PIN, HIGH);
  delayMicroseconds(30);
  pinMode(DHT_PIN, INPUT_PULLUP);

  /* Wait for sensor response: ~80 us low then ~80 us high. */
  unsigned long timeout;

  timeout = micros();
  while (digitalRead(DHT_PIN) == HIGH) {
    if ((unsigned long)(micros() - timeout) > 100) return false;
  }
  timeout = micros();
  while (digitalRead(DHT_PIN) == LOW) {
    if ((unsigned long)(micros() - timeout) > 120) return false;
  }
  timeout = micros();
  while (digitalRead(DHT_PIN) == HIGH) {
    if ((unsigned long)(micros() - timeout) > 120) return false;
  }

  /* Read 40 bits. A bit is: ~50 us low, then high whose width encodes the
   * value (~26-28 us = 0, ~70 us = 1). */
  for (uint8_t i = 0; i < 40; ++i) {
    /* Start-of-bit low period. */
    timeout = micros();
    while (digitalRead(DHT_PIN) == LOW) {
      if ((unsigned long)(micros() - timeout) > 80) return false;
    }
    /* Measure high pulse width. */
    unsigned long highStart = micros();
    timeout = micros();
    while (digitalRead(DHT_PIN) == HIGH) {
      if ((unsigned long)(micros() - timeout) > 120) return false;
    }
    unsigned long highLen = micros() - highStart;

    bytes[i / 8] <<= 1;
    if (highLen > 45) {           /* long high -> logic 1                  */
      bytes[i / 8] |= 1;
    }
  }

  /* Verify checksum. */
  uint8_t sum = bytes[0] + bytes[1] + bytes[2] + bytes[3];
  if (sum != bytes[4]) {
    return false;
  }

  *humidity = bytes[0];
  *tempC    = (int8_t)bytes[2];
  return true;
}

void Sensors::readDHT() {
  SensorData &s = g_state.sensors();
  int8_t  t = 0;
  uint8_t h = 0;
  if (dhtRead(&t, &h)) {
    s.temperatureC = t;
    s.humidity     = h;
    s.dhtValid     = true;
  } else {
    s.dhtValid = false;
  }
}
