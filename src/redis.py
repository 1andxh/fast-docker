import redis
from src.config import config

REDIS_URL = config.REDIS_URL

redis_client = redis.from_url(REDIS_URL, decode_responses=True)
