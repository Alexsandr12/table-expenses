import redis

redis_conn = redis.Redis()


def recording_dollar_value(dollar_value):
    redis_conn.setex("dollar", 3600, dollar_value)


def check_dollar_value():
    return redis_conn.get("dollar")
