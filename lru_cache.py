"""
In-Memory Key-Value Store with LRU Cache
Features: O(1) get/put, TTL expiry, disk persistence, thread-safety
"""
import time
import json
import pickle
import threading


class Node:
    def __init__(self, key=None, value=None, expiry=None):
        self.key = key
        self.value = value
        self.expiry = expiry  # absolute timestamp or None
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity=100, persist_file="cache_data.pkl"):
        self.capacity = capacity
        self.cache = {}  # key -> Node
        self.lock = threading.Lock()
        self.persist_file = persist_file

        # dummy head/tail for doubly linked list
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

        self._load_from_disk()

    # ---------- internal linked-list helpers ----------
    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def _is_expired(self, node):
        return node.expiry is not None and time.time() > node.expiry

    # ---------- public API ----------
    def get(self, key):
        with self.lock:
            node = self.cache.get(key)
            if not node:
                return None
            if self._is_expired(node):
                self._remove(node)
                del self.cache[key]
                return None
            self._remove(node)
            self._add_to_front(node)
            return node.value

    def put(self, key, value, ttl=None):
        """ttl: seconds until expiry, or None for no expiry"""
        with self.lock:
            expiry = time.time() + ttl if ttl else None

            if key in self.cache:
                node = self.cache[key]
                node.value = value
                node.expiry = expiry
                self._remove(node)
                self._add_to_front(node)
                return

            if len(self.cache) >= self.capacity:
                lru = self.tail.prev
                self._remove(lru)
                del self.cache[lru.key]

            node = Node(key, value, expiry)
            self.cache[key] = node
            self._add_to_front(node)

    def delete(self, key):
        with self.lock:
            node = self.cache.get(key)
            if node:
                self._remove(node)
                del self.cache[key]

    # ---------- persistence ----------
    def save_to_disk(self):
        with self.lock:
            data = {k: (n.value, n.expiry) for k, n in self.cache.items()}
            with open(self.persist_file, "wb") as f:
                pickle.dump(data, f)

    def _load_from_disk(self):
        try:
            with open(self.persist_file, "rb") as f:
                data = pickle.load(f)
            for k, (v, exp) in data.items():
                if exp is None or time.time() < exp:
                    node = Node(k, v, exp)
                    self.cache[k] = node
                    self._add_to_front(node)
        except (FileNotFoundError, EOFError):
            pass


# ---------- quick demo / smoke test ----------
if __name__ == "__main__":
    cache = LRUCache(capacity=3)

    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    print("get a:", cache.get("a"))  # 1, moves 'a' to front

    cache.put("d", 4)  # evicts 'b' (least recently used)
    print("get b (should be None, evicted):", cache.get("b"))

    cache.put("temp", "expires soon", ttl=2)
    print("get temp (immediately):", cache.get("temp"))
    time.sleep(3)
    print("get temp (after 3s, should be None):", cache.get("temp"))

    cache.save_to_disk()
    print("Saved to disk. Reload a new instance to test persistence.")

    # concurrency smoke test
    def worker(i):
        cache.put(f"key{i}", i)
        cache.get(f"key{i}")

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print("Concurrent access test completed without errors.")