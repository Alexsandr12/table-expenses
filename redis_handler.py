import redis

redis_conn = redis.Redis()


def recording_dollar_value(dollar_value: str) -> None:
    """Запись значения доллара

    Args:
        dollar_value: значение доллара
    """
    redis_conn.setex("dollar", 3600, dollar_value)


def check_dollar_value() -> bytes:
    """Проверка наличия значения доллара в кэш

    Return:
        bytes: значение доллара
        """
    return redis_conn.get("dollar")
