import os
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import redis
from rq import Worker, Queue, Connection


listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
#conn = redis.from_url(redis_url)

redis_host = os.environ.get('REDIS_HOST', 'localhost')    
# Channel layer definitions
# http://channels.readthedocs.org/en/latest/deploying.html#setting-up-a-channel-backend
CHANNEL_LAYERS = {
    "default": {
        # This example app uses the Redis channel layer implementation asgi_redis
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(redis_host, 6379)],
        },
        "ROUTING": "multichat.routing.channel_routing",
    },
}

#if __name__=='__main__':
    #with Connection(conn):
       # worker = Worker(map(Queue, listen))
       # worker.work()
