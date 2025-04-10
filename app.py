from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = 'database.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercicio TEXT NOT NULL,
                serie INTEGER NOT NULL,
                carga REAL NOT NULL,
                reps INTEGER NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT exercicio, serie, carga, reps, data
            FROM series
            ORDER BY data DESC, exercicio, serie
        ''')
        series = cursor.fetchall()
    return render_template('index.html', series=series)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    exercicio = request.form['exercicio']
    serie = int(request.form['serie'])
    carga = float(request.form['carga'])
    reps = int(request.form['reps'])
    data = datetime.now().strftime('%Y-%m-%d')

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO series (exercicio, serie, carga, reps, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (exercicio, serie, carga, reps, data))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/dados')
def dados():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT exercicio, data, AVG(carga) as carga_media
            FROM series
            GROUP BY exercicio, data
            ORDER BY data ASC
        ''')
        rows = cursor.fetchall()

    dados_formatados = {}
    for exercicio, data, carga in rows:
        if exercicio not in dados_formatados:
            dados_formatados[exercicio] = {"datas": [], "cargas": []}
        dados_formatados[exercicio]["datas"].append(data)
        dados_formatados[exercicio]["cargas"].append(carga)

    return jsonify(dados_formatados)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
