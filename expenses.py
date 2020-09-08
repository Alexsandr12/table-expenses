import requests
import re

from flask_bootstrap import Bootstrap
from flask import Flask, request, redirect, url_for, render_template
from mysql.connector import Error

from config import ERROR_PAGE, METHODS, REDIRECT_PAGE
from db import (
    redis_conn,
    mysql_conn,
    mysql_cursor,
    get_all_data,
    get_data_to_id,
    add_line,
    delete_line_to_id,
    delete_all_lines,
    update_line
)
from logger import logger_expenses

# TODO: аннотации и описание


app = Flask(__name__)
Bootstrap(app)


def get_dollar_value() -> float:
    """Получаем значения доллара из redis, если значения нет, парсим сайт,
    для получения значения и записываем его в redis.

    Return:
        float: значение доллара.
    """
    dollar_value = redis_conn.get("dollar")
    if dollar_value is None:
        dollar_html = requests.get("https://www.banki.ru/products/currency/usd/")
        dollar_value = re.search(
            r'<div class="currency-table__large-text">(\d+.\d+)', dollar_html.text
        ).group(1)
        dollar_value = dollar_value.replace(",", ".")
    else:
        dollar_value = dollar_value.decode("utf-8", "replace")
    return float(dollar_value)


def get_line_to_id(line_id: int) -> tuple:
    """Получение кортежа с данными строки из таблицы базы данных.

    Args:
        line_id: id строки в таблице.

    Return:
        tuple: кортеж с данными строки из таблицы.
    """
    try:
       # print(get_data_to_id(line_id)) Почему не работает ???
        return get_data_to_id(line_id)[0]
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/", methods=["GET"])
def index():
    try:
        all_data = get_all_data()
        return render_template("index.html", data=all_data)
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/add_data", methods=[METHODS])
def add_data():
    form = request.form
    rubles = float(form["rub"])
    waste_or_income = form["w/i"]
    description = form["desc"]
    dollars = round(rubles / get_dollar_value(), 2)
    try:
        add_line(rubles, dollars, waste_or_income, description)
        logger_expenses.debug(f"Добавлена строка с данными: "
                              f"rubles = {rubles}, dollars = {dollars}, "
                              f"w/i = {waste_or_income}, description = {description}"
                              )
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/delete_data", methods=[METHODS])
def delete_data():
    line_id = int(request.form["id"])
    delete_line = get_data_to_id(line_id)[0]
    logger_expenses.debug(f"Запрос на удаление строки с id {line_id}, данные строки: "
                          f"rubles = {delete_line[1]}, dollars = {delete_line[2]}, date = {delete_line[3]}, "
                          f"w/i = {delete_line[4]}, description = {delete_line[5]}"
                          )
    try:
        delete_line_to_id(line_id)
        logger_expenses.debug(f"Удалена строка с id {line_id}")
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/delete_all_data", methods=[METHODS])
def delete_all_data():
    try:
        delete_all_lines()
        logger_expenses.debug(f"Все данные удалены")
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/update_data", methods=[METHODS])
def update_data():
    line_id = int(request.form["id"])
    line_to_id = get_line_to_id(line_id)
    logger_expenses.debug(f"Запрос на изменение данных в строке с id {line_id}: "
                          f"rubles = {line_to_id[1]}, dollars = {line_to_id[2]}, date = {line_to_id[3]}, "
                          f"w/i = {line_to_id[4]}, description = {line_to_id[5]}"
                          )
    form = request.form
    if form["rub"]:
        rubles = float(form["rub"])
    else:
        rubles = line_to_id[1]

    if form["w/i"]:
        waste_or_income = form["w/i"]
    else:
        waste_or_income = line_to_id[4]

    if form["desc"]:
        description = form["desc"]
    else:
        description = line_to_id[5]

    dollars = round(rubles / get_dollar_value(), 2)
    try:
        update_line(rubles, waste_or_income, description, dollars, line_id)
        line_to_id = get_line_to_id(line_id)
        logger_expenses.debug(f"Данные изменены на: "
                              f"rubles = {line_to_id[1]}, dollars = {line_to_id[2]}, date = {line_to_id[3]}, "
                              f"w/i = {line_to_id[4]}, description = {line_to_id[5]}"
                              )
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


if __name__ == "__main__":
    app.run()
