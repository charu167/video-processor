from redis import Redis
import json
from config.config import REDIS_HOST, REDIS_PASSWORD


class Redis_servcie:
    # Initiaize redis client
    def __init__(self) -> None:
        self.client = Redis(
            host=REDIS_HOST,
            port=12944,
            decode_responses=True,
            username="default",
            password=REDIS_PASSWORD,
        )

    # RPOP
    def pop_queue(self, queue_name: str):
        job = self.client.rpop(name=queue_name)
        return json.loads(job)

    # Return the listener
    def pubsub_listener(self, channel_name):
        pubsub = self.client.pubsub()
        pubsub.subscribe(channel_name)
        print(f"Subscribed to {channel_name}. Listening for messages...")
        return pubsub
