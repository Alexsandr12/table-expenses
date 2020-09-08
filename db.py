import redis
import mysql.connector

from config import HOST, USER, PASSWORD, DATABASE, TABLE_NAME

redis_conn = redis.Redis()

mysql_conn = mysql.connector.connect(
    host=HOST, user=USER, password=PASSWORD, database=DATABASE
)
mysql_cursor = mysql_conn.cursor()

# TODO: Traceback почему появляется в файле?


def get_all_data() -> list:
    """Получение всех данных из таблицы базы данных.

    Return:
         list: Все данные таблицы.
    """
    query = f"SELECT * FROM {TABLE_NAME}"
    mysql_cursor.execute(query)
    return mysql_cursor.fetchall()


def get_data_to_id(line_id: int) -> list:
    """Получение значений из таблицы базы данных по заданному id.

    Args:
        line_id: id строки в таблице.

    Return:
        list: Данные строки из таблицы по заданному id.
    """
    query = f"SELECT * FROM {TABLE_NAME} WHERE id = {line_id}"
    mysql_cursor.execute(query)
    return mysql_cursor.fetchall()


def add_line(rubles: float, dollars: float, waste_or_income: str, description: str):
    """Добавление новой строки в таблицу базы данных.

    Args:
        rubles: рубли.
        dollars: доллары.
        waste_or_income: расход или доход.
        description: описание.
    """
    query = f"""INSERT INTO expenses 
    ( rubles, dollars, date_time, waste_or_income, description ) 
    VALUES ( %s, %s, NOW(), %s, %s)"""
    mysql_cursor.execute(query, (rubles, dollars, waste_or_income, description))
    mysql_conn.commit()


def delete_line_to_id(line_id: int):
    """Удаление строки в таблице базы данных.

    Args:
        line_id: id строки в таблице.
    """
    query = f"DELETE FROM {TABLE_NAME} WHERE id = {line_id}"
    mysql_cursor.execute(query)
    mysql_conn.commit()


def delete_all_lines():
    """Удаление всех данных таблицы в базе данных."""
    query = f"DELETE FROM {TABLE_NAME}"
    mysql_cursor.execute(query)
    mysql_conn.commit()


def update_line(
    rubles: float, waste_or_income: str, description: str, dollars: float, line_id: int
):
    """Обновление данных строки в таблице expenses базы данных.

    Args:
        rubles: рубли.
        waste_or_income: расход или доход.
        description: описание.
        dollars: доллары.
        line_id: id строки в таблице.

    """
    query = """UPDATE expenses SET
        rubles = %s,
        waste_or_income = %s,
        description = %s,
        dollars = %s,
        date_time = NOW()
        WHERE id = %s"""
    mysql_cursor.execute(
        query, (rubles, waste_or_income, description, dollars, line_id)
    )
    mysql_conn.commit()
