from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import psycopg2
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Use uma variável de ambiente em produção

# Conexão com banco PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                nome TEXT UNIQUE NOT NULL,
                role TEXT DEFAULT 'user'
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                usuario_id INTEGER REFERENCES usuarios(id)
            );
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id SERIAL PRIMARY KEY,
                exercicio_id INTEGER REFERENCES exercicios(id),
                usuario_id INTEGER REFERENCES usuarios(id),
                serie INTEGER,
                carga REAL,
                reps INTEGER,
                data DATE
            );
        ''')
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nome = request.form['nome'].strip().lower()

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, role FROM usuarios WHERE nome = %s", (nome,))
            user = cur.fetchone()
            if not user:
                cur.execute("INSERT INTO usuarios (nome) VALUES (%s) RETURNING id", (nome,))
                user = cur.fetchone()
                conn.commit()
                role = 'user'
            else:
                role = user[1]

        session['usuario_id'] = user[0]
        session['usuario_nome'] = nome
        session['role'] = role

        return redirect(url_for('index'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/index')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('SELECT id, nome FROM exercicios WHERE usuario_id = %s ORDER BY nome', (session['usuario_id'],))
        exercicios = cur.fetchall()

        cur.execute('''
            SELECT e.nome, s.serie, s.carga, s.reps, s.data
            FROM series s
            JOIN exercicios e ON s.exercicio_id = e.id
            WHERE s.usuario_id = %s
            ORDER BY s.data DESC, e.nome, s.serie
        ''', (session['usuario_id'],))
        series = cur.fetchall()

    return render_template('index.html', exercicios=exercicios, series=series, usuario=session['usuario_nome'])

@app.route('/adicionar_exercicio', methods=['POST'])
def adicionar_exercicio():
    nome = request.form['novo_exercicio'].strip()
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO exercicios (nome, usuario_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        ''', (nome, session['usuario_id']))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/adicionar', methods=['POST'])
def adicionar():
    if 'usuario_id' not in session:
        return redirect(url_for('home'))

    exercicio_id = int(request.form['exercicio_id'])
    serie = int(request.form['serie'])
    carga = float(request.form['carga'])
    reps = int(request.form['reps'])
    data = datetime.now().date()

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO series (exercicio_id, usuario_id, serie, carga, reps, data)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (exercicio_id, session['usuario_id'], serie, carga, reps, data))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/dados')
def dados():
    if 'usuario_id' not in session:
        return jsonify({})

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute('''
            SELECT e.nome, s.data, AVG(s.carga)
            FROM series s
            JOIN exercicios e ON s.exercicio_id = e.id
            WHERE s.usuario_id = %s
            GROUP BY e.nome, s.data
            ORDER BY s.data
        ''', (session['usuario_id'],))
        rows = cur.fetchall()

    dados_formatado = {}
    for nome, data, carga in rows:
        if nome not in dados_formatado:
            dados_formatado[nome] = {"datas": [], "cargas": []}
        dados_formatado[nome]["datas"].append(data.strftime('%Y-%m-%d'))
        dados_formatado[nome]["cargas"].append(carga)

    return jsonify(dados_formatado)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
