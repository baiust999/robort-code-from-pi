/**
 * robot_state.h
 * -----------------------------------------------------------------------------
 * Central finite-state machine and shared runtime state for the robot. Every
 * module reads/writes robot state through this singleton so that safety logic
 * (dead-man timer, panic, emergency stop) has one authoritative source.
 * -----------------------------------------------------------------------------
 */

#ifndef ROBOT_STATE_H
#define ROBOT_STATE_H

#include <Arduino.h>

/* High-level operating modes of the robot. */
enum RobotMode {
  MODE_BOOT = 0,   /* powering up, running self-check                 */
  MODE_READY,      /* idle, motors stopped, awaiting commands         */
  MODE_ACTIVE,     /* executing a motion command                      */
  MODE_ESTOP,      /* emergency stop latched (operator commanded)     */
  MODE_PANIC       /* fault detected (gas / comms loss / sensor)      */
};

/* Reason codes describing why the robot entered a fault/stop state. */
enum FaultReason {
  FAULT_NONE = 0,
  FAULT_DEADMAN,       /* comms timeout                               */
  FAULT_GAS,           /* MQ-136 over threshold                       */
  FAULT_OPERATOR_ESTOP /* operator issued S/emergency                 */
};

/* Aggregated live sensor readings, updated by the sensors module. */
struct SensorData {
  uint16_t distanceCm;   /* HC-SR04 forward distance (cm)             */
  bool     motion;       /* HC-SR501 PIR motion detected              */
  int8_t   temperatureC; /* DHT11 temperature (deg C)                 */
  uint8_t  humidity;     /* DHT11 relative humidity (%)               */
  uint16_t gasRaw;       /* MQ-136 raw ADC (0-1023)                   */
  bool     gasAlarm;     /* true when gasRaw >= threshold             */
  bool     dhtValid;     /* last DHT read succeeded                   */
};

class RobotState {
 public:
  RobotState();

  void init();

  /* --- Mode management ---------------------------------------------------- */
  RobotMode mode() const           { return _mode; }
  void      setMode(RobotMode m);
  bool      isMotionAllowed() const;

  FaultReason fault() const        { return _fault; }
  void        setFault(FaultReason r);
  void        clearFault();

  /* --- Dead-man / heartbeat ---------------------------------------------- */
  void          noteCommandReceived(unsigned long now);
  unsigned long lastCommandTime() const { return _lastCmdTime; }

  /* --- Shared sensor snapshot -------------------------------------------- */
  SensorData&       sensors()       { return _sensors; }
  const SensorData& sensors() const { return _sensors; }

  /* --- Human-readable mode string for telemetry -------------------------- */
  const char* modeString() const;
  const char* faultString() const;

 private:
  RobotMode   _mode;
  FaultReason _fault;
  unsigned long _lastCmdTime;
  SensorData  _sensors;
};

/* Global singleton instance (defined in robot_state.cpp). */
extern RobotState g_state;

#endif /* ROBOT_STATE_H */
