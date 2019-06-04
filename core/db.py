import redis
from setting import redis_config

redis_client = redis.StrictRedis(**redis_config)
