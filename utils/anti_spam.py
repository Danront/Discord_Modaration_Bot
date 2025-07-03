import time
from collections import defaultdict

class AntiSpam:
    def __init__(self, threshold=5, interval=10):
        self.messages = defaultdict(list)
        self.threshold = threshold
        self.interval = interval

    def is_spam(self, user_id):
        now = time.time()
        self.messages[user_id] = [t for t in self.messages[user_id] if now - t < self.interval]
        self.messages[user_id].append(now)
        return len(self.messages[user_id]) > self.threshold