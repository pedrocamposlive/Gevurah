from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
DB_NAME = 'database.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        
        # Tabela de exercícios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        ''')

        # Tabela de séries com relação ao exercício
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercicio_id INTEGER,
                serie INTEGER,
                carga REAL,
                reps INTEGER,
                data TEXT,
                FOREIGN KEY (exercicio_id) REFERENCES exercicios(id)
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        # Listar todos os exercícios para o dropdown
        cursor.execute('SELECT id, nome FROM exercicios ORDER BY nome')
        exercicios = cursor.fetchall()

        # Listar as séries com nome do exercício
        cursor.execute('''
            SELECT e.nome, s.serie, s.carga, s.reps, s.data
            FROM series s
            JOIN exercicios e ON s.exercicio_id = e.id
            ORDER BY s.data DESC, e.nome, s.serie
        ''')
        series = cursor.fetchall()

    return render_template('index.html', exercicios=exercicios, series=series)

@app.route('/adicionar_exercicio', methods=['POST'])
def adicionar_exercicio():
    nome = request.form['novo_exercicio'].strip()

    if nome:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('INSERT INTO exercicios (nome) VALUES (?)', (nome,))
                conn.commit()
            except sqlite3.IntegrityError:
                pass  # Exercício já existe, ignorar erro

    return redirect(url_for('index'))

@app.route('/adicionar', methods=['POST'])
def adicionar():
    exercicio_id = int(request.form['exercicio_id'])
    serie = int(request.form['serie'])
    carga = float(request.form['carga'])
    reps = int(request.form['reps'])
    data = datetime.now().strftime('%Y-%m-%d')

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO series (exercicio_id, serie, carga, reps, data)
            VALUES (?, ?, ?, ?, ?)
        ''', (exercicio_id, serie, carga, reps, data))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/dados')
def dados():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT e.nome, s.data, AVG(s.carga) as carga_media
            FROM series s
            JOIN exercicios e ON s.exercicio_id = e.id
            GROUP BY e.nome, s.data
            ORDER BY s.data ASC
        ''')
        rows = cursor.fetchall()

    dados_formatados = {}
    for nome, data, carga in rows:
        if nome not in dados_formatados:
            dados_formatados[nome] = {"datas": [], "cargas": []}
        dados_formatados[nome]["datas"].append(data)
        dados_formatados[nome]["cargas"].append(carga)

    return jsonify(dados_formatados)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))  # usa a porta que o Render fornecer
    init_db()
    app.run(host='0.0.0.0', port=port, debug=True)

