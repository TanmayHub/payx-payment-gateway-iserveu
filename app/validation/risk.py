import time
from collections import defaultdict
from threading import Lock


MAX_TRANSACTIONS = 10
WINDOW_SECONDS = 300

_requests = defaultdict(list)
_lock = Lock()


def check_velocity(merchant_id: int):
    now = time.time()
    cutoff = now - WINDOW_SECONDS

    with _lock:
        timestamps = [
            timestamp
            for timestamp in _requests[merchant_id]
            if timestamp > cutoff
        ]

        if len(timestamps) >= MAX_TRANSACTIONS:
            return False

        timestamps.append(now)
        _requests[merchant_id] = timestamps

    return True