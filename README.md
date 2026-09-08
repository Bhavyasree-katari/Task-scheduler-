# Priority-Based Task Scheduler / Job Queue System

A multithreaded task scheduler built from scratch in Python, using a min-heap for priority-based execution, with retry/failure handling and logging — similar in concept to OS-level schedulers or systems like Celery.

## Features

- **Priority-Based Execution** — tasks run in order of priority using a min-heap (lower number = higher priority)
- **Multithreading** — a configurable pool of worker threads pulls and executes tasks concurrently
- **Retry / Failure Handling** — failed tasks are automatically retried up to a configurable limit, with backoff between attempts
- **Logging** — every task addition, execution, failure, and permanent failure is logged with timestamps
- **OOP Design** — uses an abstract `Task` base class (Strategy pattern), so new task types can be added by subclassing and implementing `run()`

## How It Works

- Tasks are pushed onto a **min-heap** keyed by `(priority, insertion_order, task)` — the tie-breaker ensures equal-priority tasks run in the order they were added
- A pool of **worker threads** continuously pulls the highest-priority task from the heap and executes it
- If a task's `run()` method raises an exception, the scheduler retries it (with a short delay) up to `max_retries` times before logging it as permanently failed
- A `threading.Condition` is used so workers sleep efficiently when the queue is empty, instead of busy-waiting

## Usage

```python
from task_scheduler import TaskScheduler, PrintTask

scheduler = TaskScheduler(num_workers=2)
scheduler.start()

scheduler.add_task(PrintTask("Send email", priority=1, message="Sending welcome email"))
scheduler.add_task(PrintTask("Cleanup logs", priority=5, message="Cleaning old logs"))

scheduler.stop()
```

To create a custom task, subclass `Task` and implement `run()`:

```python
from task_scheduler import Task

class MyTask(Task):
    def run(self):
        # your logic here
        pass
```

## Run the Demo

```bash
python task_scheduler.py
```

This runs a built-in demo showing priority ordering, a task that fails then succeeds on retry, and a task that fails permanently after exhausting retries.

## Tech Stack

- Python 3
- `heapq` for the min-heap priority queue
- `threading` for concurrent worker execution
- `logging` for structured logs
- No external dependencies

## Why This Project

Built to demonstrate systems-level concepts — priority scheduling, concurrency, fault tolerance via retries, and clean OOP design — the same fundamentals behind real-world job queues like Celery or OS-level process schedulers.