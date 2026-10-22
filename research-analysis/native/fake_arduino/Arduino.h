/**
 * Arduino.h -- minimal HOST-SIDE STUB of the Arduino core API.
 * -----------------------------------------------------------------------------
 * This file is NOT part of the firmware and is never flashed to a board. It
 * exists only so that the UNMODIFIED production sources under arduino/ --
 * robot_state.cpp, command_parser.cpp, motors.cpp, protocol.cpp, telemetry.cpp,
 * servos.cpp, utils.cpp -- can be compiled and linked into a native x86/ARM
 * test binary on the development host, so the dead-man timer and command
 * pipeline can be exercised as real compiled C++ against the real source,
 * without an Arduino board.
 *
 * It implements just enough of the Arduino surface that those .cpp files
 * reference: digital/analog I/O (recorded, not physically driven), millis(),
 * and a Serial object with an injectable RX queue and a capturable TX buffer.
 * Nothing here changes, patches, or reimplements any decision logic from the
 * firmware; it only stands in for the hardware I/O the real logic calls.
 * -----------------------------------------------------------------------------
 */

#ifndef FAKE_ARDUINO_H
#define FAKE_ARDUINO_H

#include <stdint.h>
#include <stdlib.h>
#include <string>
#include <deque>
#include <unordered_map>

/* --- Digital I/O constants (match the real Arduino core) ------------------ */
#define HIGH 1
#define LOW  0
#define INPUT  0
#define OUTPUT 1
#define INPUT_PULLUP 2

/* Analog input pin numbers (Uno: A0-A5 = digital pins 14-19). */
#define A0 14
#define A1 15
#define A2 16
#define A3 17
#define A4 18
#define A5 19

#ifndef NULL
#define NULL 0
#endif

/* --- Recorded pin state, inspectable from the test harness ---------------- */
namespace fake_hw {
extern std::unordered_map<int, int> digitalState;   /* pin -> HIGH/LOW        */
extern std::unordered_map<int, int> analogState;    /* pin -> last PWM value  */
extern std::unordered_map<int, int> pinModeState;   /* pin -> INPUT/OUTPUT    */
extern unsigned long fakeMillis;                    /* controllable clock    */
void reset();
}

inline void pinMode(int pin, int mode) { fake_hw::pinModeState[pin] = mode; }
inline void digitalWrite(int pin, int value) { fake_hw::digitalState[pin] = value; }
inline int digitalRead(int pin) {
  auto it = fake_hw::digitalState.find(pin);
  return it == fake_hw::digitalState.end() ? LOW : it->second;
}
inline void analogWrite(int pin, int value) { fake_hw::analogState[pin] = value; }

inline unsigned long millis() { return fake_hw::fakeMillis; }

/* abs() as the real toolchain's <cstdlib> provides it for ints. */
inline int abs(int v) { return v < 0 ? -v : v; }

/* --- Fake Serial: RX is a byte queue the test fills; TX is a string the
 * test reads back and clears. Mirrors the small subset of HardwareSerial
 * used by telemetry.cpp / command_parser.cpp. ---------------------------- */
class FakeSerial {
 public:
  void begin(unsigned long) {}

  int available() { return (int)_rx.size(); }
  int read() {
    if (_rx.empty()) return -1;
    uint8_t c = _rx.front();
    _rx.pop_front();
    return c;
  }

  void print(const char *s) { _tx += s; }
  void print(char c) { _tx += c; }
  template <typename T> void print(T v) { _tx += std::to_string(v); }

  void println() { _tx += '\n'; }
  void println(const char *s) { _tx += s; _tx += '\n'; }
  void println(char c) { _tx += c; _tx += '\n'; }
  template <typename T> void println(T v) { print(v); _tx += '\n'; }

  /* --- test-only helpers, not part of the real HardwareSerial API -------- */
  void testInjectLine(const std::string &line) {
    for (char c : line) _rx.push_back((uint8_t)c);
    _rx.push_back((uint8_t)'\n');
  }
  std::string testTakeTx() {
    std::string out = _tx;
    _tx.clear();
    return out;
  }

 private:
  std::deque<uint8_t> _rx;
  std::string _tx;
};

extern FakeSerial Serial;

#endif /* FAKE_ARDUINO_H */
