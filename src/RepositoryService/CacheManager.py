import redis
import json


class CacheManager:
    def __init__(self, host="", port=6379):
        self.host = host
        self.port = port

    def get_raw(self, cache_key):
        r = redis.Redis(self.host, self.port)
        val = r.get(cache_key)
        if val is None:
            return None

        return val

    def set_raw(self, cache_key, value, ttl):
        r = redis.Redis(self.host, self.port)
        r.set(cache_key, value, ttl)

    def get_json(self, cache_key):
        r = redis.Redis(self.host, self.port)
        val = r.get(cache_key)
        if val is None:
            return None

        data = json.loads(val.decode('utf-8'))
        return data

    def set_json(self, cache_key, value, ttl):
        data = json.dumps(value)
        r = redis.Redis(self.host, self.port)
        r.set(cache_key, data.encode('utf-8'), ttl)