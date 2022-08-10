import os
import sys
sys.path.append('/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages')
import redis
from rq import Worker, Queue, Connection

listen = ['high', 'default', 'low']

#redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

#conn = redis.from_url(redis_url)

redis_url = os.getenv('REDISTOGO_URL')urlparse.uses_netloc.append('redis')
url = urlparse.urlparse(redis_url)
conn = Redis(host=url.hostname, port=url.port, db=0, password=url.password)

if __name__=='__main__':
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
