import json
from src.redis import redis_client

QUEUE_NAME = "jobs:default"


def enqueue(job: dict):
    redis_client.lpush(QUEUE_NAME, json.dumps(job))


def dequeue():
    _, job = redis_client.brpop(QUEUE_NAME)
    return json.loads(job)


# async?
