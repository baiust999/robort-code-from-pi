/**
 * scheduler.h
 * -----------------------------------------------------------------------------
 * Cooperative, non-blocking millis()-based task scheduler. Each task registers
 * a callback and a period; the scheduler invokes callbacks when their period
 * has elapsed. No preemption, no delay() — every callback must return quickly.
 * -----------------------------------------------------------------------------
 */

#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <Arduino.h>

/* Signature for a scheduled task callback. */
typedef void (*TaskFn)(void);

#define SCHEDULER_MAX_TASKS  8

struct Task {
  TaskFn        fn;
  unsigned long period;
  unsigned long last;
  bool          enabled;
};

class Scheduler {
 public:
  Scheduler();

  /* Register a periodic task. Returns the task index, or -1 if the table
   * is full. */
  int  addTask(TaskFn fn, unsigned long periodMs);

  /* Run any due tasks. Call this once per loop() iteration. */
  void run(unsigned long now);

  void enable(int index, bool on);

 private:
  Task    _tasks[SCHEDULER_MAX_TASKS];
  uint8_t _count;
};

extern Scheduler g_scheduler;

#endif /* SCHEDULER_H */
