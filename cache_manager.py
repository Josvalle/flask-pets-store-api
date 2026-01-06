import redis
import json
from functools import wraps
from flask import jsonify, request
from authenticator import JWT_Manager 



class CacheManager:
    def __init__(self, host, port, password, *args, **kwargs):
        self.redis_client = redis.Redis(
            host=host,
            port=port,
            password=password,
            *args,
            **kwargs,
        )
        connection_status = self.redis_client.ping()
        if connection_status:
            print("Connection created succesfully first")

    def store_data(self, key, value, time_to_live=None):
        try:
            if time_to_live is None:
                self.redis_client.set(key, json.dumps(value))
                
            else:
                self.redis_client.setex(key, time_to_live, value)
        except redis.RedisError as error:
            print(f" An error ocurred while storing data in Redis: {error}")

    def check_key(self, key):
        try:
            key_exists = self.redis_client.exists(key)
            if key_exists:
                return True
            return False
        except redis.RedisError as error:
            print(f"check key An error ocurred while checking a key in Redis: {error}")
            return False

    def get_data(self, key):
        try:
            output = self.redis_client.get(key)
            if output is not None:
                result = json.loads(output.decode("utf-8"))
                return result
            else:
                return None
        except redis.RedisError as error:
            print(f"get data An error ocurred while retrieving data from Redis: {error}")

    def delete_data(self, key):
        try:
            output = self.redis_client.delete(key)
            return output == 1
        except redis.RedisError as error:
            print(f"An error ocurred while deleting data from Redis: {error}")
            return False

    def delete_data_with_pattern(self, pattern):
        try:
            for key in self.redis_client.scan_iter(match=pattern):
                self.delete_data(key)
        except redis.RedisError as error:
            print(f"An error ocurred while deleting data from Redis: {error}")

cache = CacheManager('PLACEHOLDER','PLACEHOLDER','PLACEHOLDER')

jwt_manager = JWT_Manager()

def check_cache(key, combine):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if combine:
                    token = request.headers.get('Authorization')
                    token = token.replace("Bearer ","")
                    decoded = jwt_manager.decode(token)
                    user_id = decoded['id']
                    final_key = f'{key}_{user_id}'
                else:  
                    final_key = key

                exists = cache.check_key(final_key)
                if exists:
                    data = cache.get_data(final_key)
                    return jsonify(data), 200
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Error: {e}")
                return None
    
        return wrapper
    return decorator
