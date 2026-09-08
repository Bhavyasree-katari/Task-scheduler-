# In-Memory Key-Value Store with LRU Cache

A Redis-style in-memory key-value store built from scratch in Python, featuring O(1) get/put operations, LRU (Least Recently Used) eviction, TTL-based expiry, disk persistence, and thread-safe concurrent access.

## Features

- **O(1) Get/Put** — implemented using a HashMap + Doubly Linked List, avoiding built-in shortcuts like `OrderedDict` or `functools.lru_cache`
- **LRU Eviction** — automatically removes the least recently used item when the cache reaches capacity
- **TTL (Time-To-Live) Expiry** — keys can be set to expire after a given number of seconds
- **Disk Persistence** — cache state can be saved to and restored from disk using `pickle`
- **Thread-Safe** — all read/write operations are protected with locks for safe concurrent access

## How It Works

- A **doubly linked list** maintains the order of usage — most recently used items stay near the head, least recently used near the tail
- A **HashMap** maps each key directly to its node in the linked list, enabling O(1) lookups
- On every `get` or `put`, the accessed node is moved to the front of the list
- When the cache is full, the node at the tail (least recently used) is evicted

## Usage

```python
from lru_cache import LRUCache

cache = LRUCache(capacity=3)

cache.put("a", 1)
cache.put("b", 2)
cache.put("c", 3)

cache.get("a")          # returns 1, marks 'a' as recently used
cache.put("d", 4)       # evicts 'b' (least recently used)

cache.put("temp", "value", ttl=5)   # expires after 5 seconds

cache.save_to_disk()    # persist current cache state
```

## Run the Demo

```bash
python lru_cache.py
```

This runs a built-in smoke test covering eviction order, TTL expiry, persistence, and concurrent thread-safe access.

## Tech Stack

- Python 3
- `threading` for concurrency and locks
- `pickle` for disk persistence
- No external dependencies

## Why This Project

Built to demonstrate core data structure design (HashMap + Doubly Linked List) and systems-level concepts like caching, expiry, persistence, and thread safety — concepts directly used in real-world systems like Redis and Memcached.