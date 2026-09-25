/**
 * config.h
 * -----------------------------------------------------------------------------
 * Central hardware and firmware configuration for the robot's Arduino UNO
 * firmware. All pin assignments, timing constants and tunable parameters live
 * here so the rest of the codebase never hard-codes magic numbers.
 *
 * Target board : Arduino UNO (ATmega328P)
 * Clock        : 16 MHz
 * -----------------------------------------------------------------------------
 */

#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

/* ===========================================================================
 * FIRMWARE IDENTIFICATION
 * ======================================================================== */
#define FW_NAME              "RESCUE-UNO"
#define FW_VERSION           "1.0.0"

/* ===========================================================================
 * SERIAL / UART CONFIGURATION
 * ======================================================================== */
#define SERIAL_BAUD          115200UL
#define RX_BUFFER_SIZE       32       /* max bytes for one inbound command   */
#define CMD_TERMINATOR       '\n'     /* commands terminated by newline      */

/* ===========================================================================
 * SCHEDULER TIMING (all values in milliseconds)
 * ======================================================================== */
#define DEADMAN_TIMEOUT_MS       2000UL  /* stop motors if no cmd in window  */
#define HEARTBEAT_PERIOD_MS      1000UL  /* emit heartbeat telemetry         */
#define TELEMETRY_PERIOD_MS       500UL  /* periodic status broadcast        */
#define SENSOR_FAST_PERIOD_MS      50UL  /* ultrasonic + IR polling          */
#define SENSOR_SLOW_PERIOD_MS    2000UL  /* DHT11 + gas (slow sensors)       */
#define MOTOR_SERVICE_PERIOD_MS    10UL  /* motor ramp / safety service      */

/* ===========================================================================
 * MOTOR DRIVER (BTS7960 dual half-bridge) PIN MAP
 * Two BTS7960 drivers: one per side (differential drive).
 * Each BTS7960 exposes RPWM (forward) and LPWM (reverse) inputs.
 * EN pins are tied together and driven by a single enable line.
 * ======================================================================== */
#define LEFT_RPWM_PIN         5    /* PWM capable */
#define LEFT_LPWM_PIN         6    /* PWM capable */
#define RIGHT_RPWM_PIN        9    /* PWM capable */
#define RIGHT_LPWM_PIN       10    /* PWM capable */
#define MOTOR_EN_PIN          4    /* common enable for both drivers        */

#define MOTOR_PWM_MIN         0
#define MOTOR_PWM_MAX         255
#define MOTOR_SPEED_MIN       0    /* protocol speed range (0-255)          */
#define MOTOR_SPEED_MAX       255

/* Ramp rate: PWM units changed per motor-service tick to avoid current spikes */
#define MOTOR_RAMP_STEP       15

/* ===========================================================================
 * SERVO PIN MAP (pan / tilt camera gimbal)
 * ======================================================================== */
#define SERVO_PAN_PIN        11
#define SERVO_TILT_PIN        3

#define SERVO_ANGLE_MIN       0
#define SERVO_ANGLE_MAX     180
#define SERVO_PAN_HOME       90
#define SERVO_TILT_HOME      90

/* ===========================================================================
 * SENSOR PIN MAP
 * ======================================================================== */
/* HC-SR04 ultrasonic distance */
#define ULTRASONIC_TRIG_PIN   7
#define ULTRASONIC_ECHO_PIN   8    /* echo -> uses pulseIn                   */

/* HC-SR501 PIR motion sensor */
#define PIR_PIN               2    /* interrupt capable (INT0)              */

/* DHT11 temperature / humidity */
#define DHT_PIN              A2
#define DHT_TYPE_DHT11        11

/* MQ-136 gas sensor (analog) */
#define GAS_PIN              A3

/* ===========================================================================
 * SENSOR THRESHOLDS / SAFETY
 * ======================================================================== */
#define ULTRASONIC_MAX_CM     400    /* HC-SR04 practical max range          */
#define ULTRASONIC_TIMEOUT_US 25000UL /* pulseIn timeout (~4.2 m)            */
#define GAS_ALARM_THRESHOLD   1000   /* raw ADC value -> gas panic - increased for testing */

/* ===========================================================================
 * STATUS LED
 * ======================================================================== */
#define STATUS_LED_PIN       13    /* on-board LED                          */

/* ===========================================================================
 * DEBUG
 * ======================================================================== */
/* Set to 1 to enable verbose debug prints (disabled for production).       */
#define DEBUG_ENABLED         0

#endif /* CONFIG_H */
