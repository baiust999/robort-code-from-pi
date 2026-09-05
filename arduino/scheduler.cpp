/**
 * scheduler.cpp
 * -----------------------------------------------------------------------------
 * Cooperative scheduler implementation. Overflow-safe timing via unsigned
 * subtraction.
 * -----------------------------------------------------------------------------
 */

#include "scheduler.h"

Scheduler g_scheduler;

Scheduler::Scheduler() : _count(0) {
  for (uint8_t i = 0; i < SCHEDULER_MAX_TASKS; ++i) {
    _tasks[i].fn      = NULL;
    _tasks[i].period  = 0;
    _tasks[i].last    = 0;
    _tasks[i].enabled = false;
  }
}

int Scheduler::addTask(TaskFn fn, unsigned long periodMs) {
  if (_count >= SCHEDULER_MAX_TASKS || fn == NULL) {
    return -1;
  }
  Task &t   = _tasks[_count];
  t.fn      = fn;
  t.period  = periodMs;
  t.last    = millis();
  t.enabled = true;
  return _count++;
}

void Scheduler::run(unsigned long now) {
  for (uint8_t i = 0; i < _count; ++i) {
    Task &t = _tasks[i];
    if (!t.enabled || t.fn == NULL) {
      continue;
    }
    if ((unsigned long)(now - t.last) >= t.period) {
      t.last = now;
      t.fn();
    }
  }
}

void Scheduler::enable(int index, bool on) {
  if (index >= 0 && index < (int)_count) {
    _tasks[index].enabled = on;
  }
}
