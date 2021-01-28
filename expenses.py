from typing import Union

from flask_bootstrap import Bootstrap
from flask import Flask, request, redirect, url_for, render_template
from mysql.connector import Error
from werkzeug.wrappers.response import Response

from config import ERROR_PAGE, METHODS, REDIRECT_PAGE
from sql_handler import (
    get_all_data,
    get_data_to_id,
    add_line,
    delete_line_to_id,
    delete_all_lines,
    update_line,
)
from logger import logger_expenses
from utilits import get_dollar_value, get_line_to_id


app = Flask(__name__)
Bootstrap(app)


@app.route("/", methods=["GET"])
def index() -> str:
    """Основной route приложения.

    Returns:
        str: html страницы.
    """
    try:
        all_data = get_all_data()
        return render_template("index.html", data=all_data)
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/add_data", methods=[METHODS])
def add_data() -> Union[Response, str]:
    """Route для добавления строки с данными в таблицу.

    Returns:
        Union[Response, str]: редирект на основную html или html-страница.
    """
    form = request.form
    rubles = float(form["rub"])
    waste_or_income = form["w/i"]
    description = form["desc"]
    dollars = round(rubles / get_dollar_value(), 2)

    try:
        add_line(rubles, dollars, waste_or_income, description)
        logger_expenses.debug(
            "Добавлена строка с данными: "
            f"rubles = {rubles}, dollars = {dollars}, "
            f"w/i = {waste_or_income}, description = {description}"
        )
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/delete_data", methods=[METHODS])
def delete_data() -> Union[Response, str]:
    """Route для удаления строки с данными в таблице.

    Returns:
        Union[Response, str]: редирект на основную html или html-страница.
    """
    line_id = int(request.form["id"])
    delete_line = get_data_to_id(line_id)[0]
    logger_expenses.debug(
        f"Запрос на удаление строки с id {line_id}, данные строки: "
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
def delete_all_data() -> Union[Response, str]:
    """Route для удаления всех строк в таблице.

    Returns:
        Union[Response, str]: редирект на основную html или html-страница.
    """
    try:
        delete_all_lines()
        logger_expenses.debug(f"Все данные удалены")
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


@app.route("/update_data", methods=[METHODS])
def update_data() -> Union[Response, str]:
    """Route для изменения строки с данными в таблицу.

    Returns:
        Union[Response, str]: редирект на основную html или html-страница.
    """
    line_id = int(request.form["id"])
    line_to_id = get_line_to_id(line_id)
    logger_expenses.debug(
        f"Запрос на изменение данных в строке с id {line_id}: "
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
        logger_expenses.debug(
            "Данные изменены на: "
            f"rubles = {line_to_id[1]}, dollars = {line_to_id[2]}, date = {line_to_id[3]}, "
            f"w/i = {line_to_id[4]}, description = {line_to_id[5]}"
        )
        return redirect(url_for(REDIRECT_PAGE))
    except Error as e:
        logger_expenses.error(f"Ошибка: {e}", exc_info=True)
        return render_template(ERROR_PAGE)


if __name__ == "__main__":
    app.run()
