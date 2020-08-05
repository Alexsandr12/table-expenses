import requests
import re

from flask import Flask, request, redirect, url_for, render_template
from flask_bootstrap import Bootstrap

import redis
import mysql.connector
from mysql.connector import Error


redis_conn = redis.Redis()

def get_dollar_value():
    dollar_html = requests.get('https://www.banki.ru/products/currency/usd/')
    dollar_value = re.search(r'<div class="currency-table__large-text">(\d+.\d+)', dollar_html.text).group(1)
    dollar_value = dollar_value.replace(',','.')
    return dollar_value

dollar_value = redis_conn.get('dollar')
if dollar_value is None:
    dollar_value = get_dollar_value()
    redis_conn.setex("dollar", 3600, dollar_value)
else:
    dollar_value = dollar_value.decode("utf-8", "replace")
dollar_value = float(dollar_value)


conn = mysql.connector.connect(host='localhost', user='alexandr', password='1', database='mysqltest')
cursor = conn.cursor()

def execute_data(conn, query):
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Ошибка {e}")
select_data = "SELECT * FROM expenses"
data = execute_data(conn, select_data)

def execute_data_id(conn, query):
    id = int(request.form['id'])
    result = None
    try:
        cursor.execute(query, (id,))
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Ошибка {e}")

app = Flask(__name__)
Bootstrap(app)

@app.route('/', methods=['GET'])
def index():
    return render_template('expenses.html', data=data)

@app.route('/add_data', methods=['POST'])
def add_data():
        rubles = float(request.form['rub'])
        waste_or_income = request.form['w/i']
        description = request.form['desc']
        dollars = round(rubles / dollar_value, 2)
        add_in_expenses = """INSERT INTO expenses 
        ( rubles, dollars, date_time, waste_or_income, description ) 
        VALUES ( %s, %s, NOW(), %s, %s )"""
        val = (rubles, dollars, waste_or_income, description)

        try:
            cursor.execute(add_in_expenses, val)
            conn.commit()
        except Error as e:
            print(f"хуита {e}")
        return redirect(url_for('index'))

@app.route('/delete_data', methods=['POST'])
def delete_data():
    id = int(request.form['id'])
    delete_in_expenses = "DELETE FROM expenses WHERE id = %s"
    try:
        cursor.execute(delete_in_expenses, (id,))
        conn.commit()
    except Error as e:
        print(f"хуита {e}")
    return redirect(url_for('index'))

@app.route('/delete_all_data', methods=['POST'])
def delete_all_data():
    delete_all = "DELETE FROM expenses"
    try:
        cursor.execute(delete_all)
        conn.commit()
    except Error as e:
        print(f"хуита {e}")
    return redirect(url_for('index'))

@app.route('/update_data', methods=['POST'])
def update_data():
    select_data = "SELECT * FROM expenses WHERE id = %s"
    data_id = execute_data_id(conn, select_data)
    data_id = data_id[0]

    id = int(request.form['id'])
    if request.form['rub']:
        rubles = float(request.form['rub'])
    else:
        rubles = data_id[1]

    if request.form['w/i']:
        waste_or_income = request.form['w/i']
    else:
        waste_or_income = data_id[4]

    if request.form['desc']:
        description = request.form['desc']
    else:
        description = data_id[5]

    dollars = round(rubles / dollar_value, 2)
    update_in_expenses = """UPDATE expenses SET
    rubles = %s,
    waste_or_income = %s,
    description = %s,
    dollars = %s,
    date_time = NOW()
    WHERE id = %s"""
    val = (rubles, waste_or_income, description, dollars, id)
    try:
        cursor.execute(update_in_expenses, val)
        conn.commit()
    except Error as e:
        print(f"хуита {e}")
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run()
