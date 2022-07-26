import threading


class ThreadSafeSingleton:
    _lock = threading.Lock()
    _instance = None

    @classmethod
    def instance(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = cls()
        return cls._instance

