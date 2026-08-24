from datetime import datetime, timezone
from uuid import uuid4


class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event_type, callback):
        self.subscribers.setdefault(event_type, []).append(callback)

    def publish(self, event_type, transaction_id, merchant_id, amount, data=None):
        event = {
            "event_id": str(uuid4()),
            "event_type": event_type,
            "transaction_id": transaction_id,
            "merchant_id": merchant_id,
            "amount": float(amount),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data or {},
        }

        for callback in self.subscribers.get(event_type, []):
            callback(event)

        return event


event_bus = EventBus()


def webhook_simulator(event):
    print(
        f"[WEBHOOK] {event['event_type']} "
        f"transaction={event['transaction_id']}"
    )


event_bus.subscribe(
    "txn:transaction:processing",
    webhook_simulator,
)