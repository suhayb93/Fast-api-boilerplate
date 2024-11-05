import redis
from redis.exceptions import ConnectionError
#TODO: handle if redis server does not work
try:
    global redis_interface
    redis_interface = redis.Redis(host="localhost", port=6379, decode_responses=True)
    redis_interface.ping()
    print("Connected to Redis successfully!")
except ConnectionError:
    print('redis is not working')