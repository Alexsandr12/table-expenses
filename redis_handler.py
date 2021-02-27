import redis
from typing import Union

redis_conn = redis.Redis()


def recording_dollar_value(dollar_value: str) -> None:
    """Запись значения доллара

    Args:
        dollar_value: значение доллара
    """
    redis_conn.setex("dollar", 3600, dollar_value)


def check_dollar_value() -> Union[bytes, None]:
    """Проверка наличия значения доллара в кэш

    Return:
        Union[bytes, None]: значение доллара или ничего
    """
    return redis_conn.get("dollar")
