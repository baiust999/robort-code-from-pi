/**
 * arduino.ino  --  Rescue Robot Arduino UNO Firmware
 * =============================================================================
 * Top-level sketch. Wires together the modular subsystems and implements the
 * safe boot sequence and the cooperative main loop.
 *
 * Architecture (non-blocking, cooperative):
 *   setup()               -> safe boot sequence
 *   loop()                -> parser.poll() + scheduler.run() + safety.tick()
 *
 * Scheduled tasks:
 *   taskMotorService   10 ms   PWM ramp + motor safety
 *   taskSensorFast     50 ms   ultrasonic + IR
 *   taskSensorSlow   2000 ms   DHT11 + gas
 *   taskTelemetry     500 ms   periodic telemetry line
 *   taskHeartbeat    1000 ms   heartbeat line
 *   taskSafety         10 ms   dead-man + panic supervisor
 *
 * Modules:
 *   config.h          hardware map + tunables
 *   utils             helpers
 *   robot_state       finite-state machine + shared state
 *   scheduler         cooperative millis() scheduler
 *   motors            BTS7960 differential drive
 *   servos            pan/tilt gimbal
 *   sensors           acquisition (HC-SR04, IR, PIR, DHT11, MQ-136)
 *   protocol          UART wire format
 *   command_parser    RX framing + 4-stage validation
 *   telemetry         outbound messages
 * =============================================================================
 */

#include <Arduino.h>
#include "config.h"
#include "utils.h"
#include "robot_state.h"
#include "scheduler.h"
#include "motors.h"
#include "servos.h"
#include "sensors.h"
#include "protocol.h"
#include "command_parser.h"
#include "telemetry.h"

/* ---------------------------------------------------------------------------
 * Scheduled task callbacks (thin wrappers around module service routines).
 * ------------------------------------------------------------------------- */
static void taskMotorService() {
  g_motors.service();
}

static void taskSensorFast() {
  g_sensors.serviceFast();
}

static void taskSensorSlow() {
  g_sensors.serviceSlow();
}

static void taskTelemetry() {
  g_telemetry.sendTelemetry();
}

static void taskHeartbeat() {
  g_telemetry.sendHeartbeat();
  /* Blink the status LED as a visible liveness indicator. */
  digitalWrite(STATUS_LED_PIN, !digitalRead(STATUS_LED_PIN));
}

/* ---------------------------------------------------------------------------
 * Safety supervisor: dead-man timer, obstacle guard, gas panic, and fault
 * recovery. Runs frequently (10 ms) so faults are caught promptly.
 * ------------------------------------------------------------------------- */
static void taskSafety() {
  unsigned long now = millis();
  const SensorData &s = g_state.sensors();

  /* --- Gas panic (highest priority, latching) -------------------------- */
  if (s.gasAlarm && g_state.fault() != FAULT_GAS) {
    g_state.setFault(FAULT_GAS);
    g_motors.emergencyStop();
    g_telemetry.sendPanic();
    return;
  }

  /* --- Dead-man timer: comms loss -> fail-safe shutdown ---------------- */
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

  /* --- Obstacle guard: auto-stop forward motion near an obstacle ------- */
  if (g_state.mode() == MODE_ACTIVE &&
      g_motors.direction() == DIR_FORWARD) {
    bool blocked = (s.distanceCm <= OBSTACLE_DISTANCE_CM) ||
                   s.irLeft || s.irRight;
    if (blocked) {
      g_motors.stop();
      g_state.setMode(MODE_READY);
      g_telemetry.sendEvent("OBSTACLE_STOP");
    }
  }

  /* --- Recovery: if a dead-man fault cleared because comms resumed ----- */
  if (g_state.fault() == FAULT_DEADMAN &&
      (unsigned long)(now - g_state.lastCommandTime()) < DEADMAN_TIMEOUT_MS) {
    g_state.clearFault();
    g_motors.enableDrivers(true);
    g_telemetry.sendEvent("DEADMAN_CLEARED");
  }

  /* --- Recovery: gas alarm cleared ------------------------------------- */
  if (g_state.fault() == FAULT_GAS && !s.gasAlarm) {
    g_state.clearFault();
    g_motors.enableDrivers(true);
    g_telemetry.sendEvent("GAS_CLEARED");
  }
}

/* ---------------------------------------------------------------------------
 * Safe boot sequence.
 * ------------------------------------------------------------------------- */
void setup() {
  /* 1. Status LED first so we have a visible sign of life. */
  pinMode(STATUS_LED_PIN, OUTPUT);
  digitalWrite(STATUS_LED_PIN, HIGH);

  /* 2. Bring outputs to a known-safe state BEFORE anything else can move. */
  g_motors.init();       /* drivers disabled, PWM zero                     */

  /* 3. Serial link. */
  Serial.begin(SERIAL_BAUD);

  /* 4. Shared state. */
  g_state.init();

  /* 5. Peripherals. */
  g_servos.init();       /* centre pan/tilt                                */
  g_sensors.init();      /* pins + PIR interrupt                           */
  g_parser.init();

  /* 6. Register scheduled tasks. */
  g_scheduler.addTask(taskMotorService, MOTOR_SERVICE_PERIOD_MS);
  g_scheduler.addTask(taskSafety,       MOTOR_SERVICE_PERIOD_MS);
  g_scheduler.addTask(taskSensorFast,   SENSOR_FAST_PERIOD_MS);
  g_scheduler.addTask(taskSensorSlow,   SENSOR_SLOW_PERIOD_MS);
  g_scheduler.addTask(taskTelemetry,    TELEMETRY_PERIOD_MS);
  g_scheduler.addTask(taskHeartbeat,    HEARTBEAT_PERIOD_MS);

  /* 7. Prime the dead-man timer so we don't panic on the first loop, then
   *    transition to READY and announce it. */
  g_state.noteCommandReceived(millis());
  g_state.setMode(MODE_READY);
  g_motors.enableDrivers(true);

  digitalWrite(STATUS_LED_PIN, LOW);
  g_telemetry.sendReady();
}

/* ---------------------------------------------------------------------------
 * Cooperative main loop. No blocking calls: everything is millis()-driven.
 * ------------------------------------------------------------------------- */
void loop() {
  unsigned long now = millis();
  g_parser.poll(now);      /* consume inbound commands                     */
  g_scheduler.run(now);    /* run any due periodic tasks                   */
}
