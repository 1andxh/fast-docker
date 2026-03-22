import json
from src.redis import redis_client
from typing import Optional, cast

QUEUE_NAME = "jobs:default"


def enqueue(job: dict):
    redis_client.lpush(QUEUE_NAME, json.dumps(job))


def dequeue():
    result = redis_client.brpop(QUEUE_NAME, timeout=0)
    _, job = cast(tuple[str, str], result)
    return json.loads(job)


# async?
