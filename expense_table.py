import mysql.connector
from mysql.connector import Error


conn = mysql.connector.connect(
    host="localhost", user="alexandr", password="1", database="mysqltest"
)

cursor = conn.cursor()
create_table_data = """
CREATE TABLE IF NOT EXISTS expenses (
id INT AUTO_INCREMENT,
rubles FLOAT NOT NULL,
dollars FLOAT NOT NULL,
date_time DATETIME NOT NULL,
waste_or_income TEXT NOT NULL,
description TEXT NOT NULL,
PRIMARY KEY (id)
)
"""
try:
    cursor.execute(create_table_data)
    conn.commit()
    print("Таблица создана")
except Error as e:
    print(f"{e}")
