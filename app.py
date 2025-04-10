
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = 'database.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                series INTEGER NOT NULL,
                carga REAL NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM exercicios ORDER BY data DESC')
        exercicios = cursor.fetchall()
    return render_template('index.html', exercicios=exercicios)

@app.route('/adicionar', methods=['POST'])
def adicionar():
    nome = request.form['nome']
    series = int(request.form['series'])
    carga = float(request.form['carga'])
    data = datetime.now().strftime('%Y-%m-%d')
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO exercicios (nome, series, carga, data) VALUES (?, ?, ?, ?)',
                       (nome, series, carga, data))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/dados')
def dados():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nome, data, carga FROM exercicios ORDER BY data')
        rows = cursor.fetchall()

    dados_formatados = {}
    for nome, data, carga in rows:
        if nome not in dados_formatados:
            dados_formatados[nome] = {"datas": [], "cargas": []}
        dados_formatados[nome]["datas"].append(data)
        dados_formatados[nome]["cargas"].append(carga)

    return jsonify(dados_formatados)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)
