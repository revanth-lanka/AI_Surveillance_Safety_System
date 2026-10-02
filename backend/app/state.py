import threading
import time
from collections import deque

class AppState:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = True
        self.latest_jpeg = None
        self.stats = {
            "people": 0,
            "vehicles": 0,
            "objects": 0,
            "alerts": 0,
            "fps": 0.0,
            "camera": "Camera 1",
            "status": "STARTING",
            "model": "",
        }
        self.events = deque(maxlen=100)
        self.zone = {"x1": 180, "y1": 100, "x2": 620, "y2": 420}
        self.crowd_threshold = 8
        self.confidence = 0.45
        self.last_event_times = {}
        self.last_frame_time = time.time()

    def update_stats(self, **kwargs):
        with self.lock:
            self.stats.update(kwargs)

    def snapshot(self):
        with self.lock:
            return dict(self.stats)

    def add_event_memory(self, event):
        with self.lock:
            self.events.appendleft(event)

    def memory_events(self):
        with self.lock:
            return list(self.events)

STATE = AppState()
