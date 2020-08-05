from collections import namedtuple

from flask import Flask, render_template, redirect, url_for, request


app = Flask(__name__)

Message = namedtuple('Message', 'text tag')
messages = []


@app.route('/', methods=['GET'])
def hello_world():
    return render_template('index.html')


@app.route('/main', methods=['GET'])
def main():
    return render_template('main.html', messages=messages)


@app.route('/add_message', methods=['POST'])
def add_message():
    text = request.form['text']
    tag = request.form['tag']

    messages.append(Message(text, tag))

    return redirect(url_for('main'))



МОЕЕЕЕЕ

id = int(request.form['id'])
if request.form['rub']:
    rubles = float(request.form['rub'])
else:
    rubles = data_id[1]
print(rubles)
    waste_or_income = request.form['w/i']
    description = request.form['desc']
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