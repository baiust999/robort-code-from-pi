#include "Arduino.h"

namespace fake_hw {
std::unordered_map<int, int> digitalState;
std::unordered_map<int, int> analogState;
std::unordered_map<int, int> pinModeState;
unsigned long fakeMillis = 0;

void reset() {
  digitalState.clear();
  analogState.clear();
  pinModeState.clear();
  fakeMillis = 0;
}
}  // namespace fake_hw

FakeSerial Serial;
