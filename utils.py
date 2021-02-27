import re
from typing import Union

import requests
from flask import render_template
from mysql.connector import Error
from werkzeug.wrappers.response import Response

from redis_handler import recording_dollar_value, check_dollar_value
from sql_handler import get_data_to_id
from logger import logger_expenses
from config import ERROR_PAGE


def get_dollar_value() -> float:
    """Получаем значения доллара из redis, если значения нет, парсим сайт,
    для получения значения и записываем его в redis.

    Return:
        float: значение доллара.
    """
    dollar_value_cache = check_dollar_value()
    if dollar_value_cache is None:
        dollar_html = requests.get("https://www.banki.ru/products/currency/usd/")
        dollar_value = re.search(
            r'<div class="currency-table__large-text">(\d+.\d+)', dollar_html.text
        ).group(1)
        dollar_value = dollar_value.replace(",", ".")
        recording_dollar_value(dollar_value)
    else:
        dollar_value = dollar_value_cache.decode("utf-8", "replace")

    return float(dollar_value)


def get_line_to_id(line_id: int) -> Union[tuple, Response]:
    """Получение кортежа с данными строки из таблицы базы данных.

    Args:
        line_id: id строки в таблице.

    Return:
        Union[tuple, Response]: кортеж с данными строки из таблицы или страницу с ошибкой
    """
    try:
        return get_data_to_id(line_id)[0]
    except Error as err:
        logger_expenses.error(f"Ошибка: {err}", exc_info=True)
        return render_template(ERROR_PAGE)
