from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
import os
from datetime import date
from contextlib import contextmanager

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")

DATABASE_URL = os.environ.get("DATABASE_URL")

@contextmanager
def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT UNIQUE NOT NULL,
                    role TEXT DEFAULT 'user'
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS exercicios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    usuario_id INTEGER REFERENCES usuarios(id)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS series (
                    id SERIAL PRIMARY KEY,
                    exercicio_id INTEGER REFERENCES exercicios(id),
                    usuario_id INTEGER REFERENCES usuarios(id),
                    serie INTEGER,
                    carga REAL,
                    reps INTEGER,
                    data DATE
                );
            """)
            # Seed admin fixo
            cur.execute("""
                INSERT INTO usuarios (nome, role)
                VALUES ('admin', 'admin')
                ON CONFLICT (nome) DO NOTHING;
            """)
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, role FROM usuarios WHERE nome = %s", (nome,))
                user = cur.fetchone()
                if not user:
                    cur.execute("INSERT INTO usuarios (nome) VALUES (%s) RETURNING id, role", (nome,))
                    user = cur.fetchone()
                    conn.commit()
        session['usuario_id'] = user[0]
        session['usuario_nome'] = nome
        session['role'] = user[1]
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/index')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, nome FROM exercicios WHERE usuario_id = %s", (usuario_id,))
            exercicios = cur.fetchall()
            cur.execute("""
                SELECT data, nome, serie, carga, reps
                FROM series
                JOIN exercicios ON series.exercicio_id = exercicios.id
                WHERE series.usuario_id = %s
                ORDER BY data DESC
            """, (usuario_id,))
            historico = cur.fetchall()

    return render_template('index.html', usuario_nome=session['usuario_nome'], exercicios=exercicios, historico=historico)

@app.route('/adicionar_exercicio', methods=['POST'])
def adicionar_exercicio():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    nome = request.form['nome'].strip()
    if nome:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO exercicios (nome, usuario_id) VALUES (%s, %s)", (nome, session['usuario_id']))
            conn.commit()
    return redirect(url_for('index'))

@app.route('/registrar_serie', methods=['POST'])
def registrar_serie():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    exercicio_id = request.form['exercicio_id']
    serie = request.form['serie']
    carga = request.form['carga']
    reps = request.form['reps']
    data_hoje = date.today()

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO series (exercicio_id, usuario_id, serie, carga, reps, data)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (exercicio_id, session['usuario_id'], serie, carga, reps, data_hoje))
        conn.commit()

    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    filtro = request.args.get('filtro', 'todos')

    with get_db() as conn:
        with conn.cursor() as cur:
            if filtro != 'todos':
                cur.execute("SELECT id, nome, role FROM usuarios WHERE role = %s ORDER BY id", (filtro,))
            else:
                cur.execute("SELECT id, nome, role FROM usuarios ORDER BY id")
            usuarios = cur.fetchall()

    return render_template('admin.html', usuarios=usuarios, filtro=filtro)

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    nome = request.form['nome'].strip()
    role = request.form['role']
    if nome and role:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO usuarios (nome, role) VALUES (%s, %s) ON CONFLICT (nome) DO NOTHING", (nome, role))
            conn.commit()
    return redirect(url_for('admin'))

@app.route('/alterar_usuario', methods=['POST'])
def alterar_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    user_id = request.form['id']
    novo_role = request.form['novo_role']

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE usuarios SET role = %s WHERE id = %s", (novo_role, user_id))
        conn.commit()

    return redirect(url_for('admin'))

@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    user_id = request.form['id']

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM series WHERE usuario_id = %s", (user_id,))
            cur.execute("DELETE FROM exercicios WHERE usuario_id = %s", (user_id,))
            cur.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        conn.commit()

    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
