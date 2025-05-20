import asyncio
import json
import redis.asyncio as aioredis


class RedisPubSub:
    def __init__(self, redis: aioredis.Redis):
        self.redis = redis

    async def publish_message(self, room_id: str, payload: dict):
        channel = f"chat:{room_id}"
        await self.redis.publish(channel, json.dumps(payload, ensure_ascii=False))

    async def subscribe(self, room_id: str):
        mpsc = self.redis.pubsub()
        await mpsc.subscribe(f"chat:{room_id}")
        try:
            while True:
                msg = await mpsc.get_message(ignore_subscribe_messages=True, timeout=1)
                if msg and msg["data"]:
                    yield json.loads(msg["data"])
                else:
                    await asyncio.sleep(0.1)
        finally:
            await mpsc.unsubscribe(f"chat:{room_id}")
