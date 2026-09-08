"""
Priority-Based Task Scheduler / Job Queue System
Features: Min-Heap priority queue, multithreading, retry/failure handling, logging
"""
import heapq
import threading
import time
import itertools
import logging
from abc import ABC, abstractmethod

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class Task(ABC):
    """Abstract base class for all tasks (Strategy pattern)."""
    def __init__(self, name, priority, max_retries=3):
        self.name = name
        self.priority = priority
        self.max_retries = max_retries
        self.attempts = 0

    @abstractmethod
    def run(self):
        """Subclasses implement actual work here. Raise Exception on failure."""
        pass


class PrintTask(Task):
    """Example concrete task."""
    def __init__(self, name, priority, message, fail_times=0):
        super().__init__(name, priority)
        self.message = message
        self.fail_times = fail_times  # simulate failures for testing retries

    def run(self):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise RuntimeError(f"Simulated failure #{self.attempts} for {self.name}")
        logging.info(f"Executing '{self.name}': {self.message}")


class TaskScheduler:
    def __init__(self, num_workers=3):
        self._heap = []
        self._counter = itertools.count()  # tie-breaker for equal priorities
        self._lock = threading.Lock()
        self._condition = threading.Condition(self._lock)
        self._num_workers = num_workers
        self._workers = []
        self._running = False

    def add_task(self, task: Task):
        with self._condition:
            # lower number = higher priority (min-heap)
            heapq.heappush(self._heap, (task.priority, next(self._counter), task))
            logging.info(f"Task added: {task.name} (priority={task.priority})")
            self._condition.notify()

    def _worker_loop(self):
        while self._running:
            with self._condition:
                while not self._heap and self._running:
                    self._condition.wait(timeout=0.5)
                if not self._running:
                    return
                if not self._heap:
                    continue
                _, _, task = heapq.heappop(self._heap)

            self._execute_with_retry(task)

    def _execute_with_retry(self, task: Task):
        while task.attempts < task.max_retries:
            try:
                task.run()
                return
            except Exception as e:
                logging.warning(f"Task '{task.name}' failed (attempt {task.attempts}): {e}")
                time.sleep(0.5)  # backoff before retry
        logging.error(f"Task '{task.name}' permanently failed after {task.max_retries} attempts")

    def start(self):
        self._running = True
        for i in range(self._num_workers):
            t = threading.Thread(target=self._worker_loop, daemon=True, name=f"Worker-{i}")
            t.start()
            self._workers.append(t)
        logging.info(f"Scheduler started with {self._num_workers} workers")

    def stop(self):
        with self._condition:
            self._running = False
            self._condition.notify_all()
        for t in self._workers:
            t.join()
        logging.info("Scheduler stopped")


# ---------- quick demo / smoke test ----------
if __name__ == "__main__":
    scheduler = TaskScheduler(num_workers=2)
    scheduler.start()

    scheduler.add_task(PrintTask("Low priority job", priority=5, message="Doing low priority work"))
    scheduler.add_task(PrintTask("High priority job", priority=1, message="Doing high priority work"))
    scheduler.add_task(PrintTask("Retry job", priority=2, message="Succeeds on 2nd try", fail_times=1))
    scheduler.add_task(PrintTask("Always fails", priority=3, message="Never succeeds", fail_times=99))

    time.sleep(3)  # let workers process
    scheduler.stop()