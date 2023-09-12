import redis

class RedisServer:
    def __init__(self,host,port,password=None):
        self.host = host
        self.port = port
        self.password = password

    def redis_connect(self):
        return redis.Redis(host='127.0.0.1', port=6379)


