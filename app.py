from flask import Flask, render_template, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from datetime import date
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "devkey")

DATABASE = 'database.db'

# ---------------- DB Connection ----------------
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------------- DB Init ----------------
def init_db():
    with app.app_context():
        db = get_db()
        cur = db.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                coach_id INTEGER,
                FOREIGN KEY (coach_id) REFERENCES usuarios(id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exercicio_id INTEGER,
                usuario_id INTEGER,
                serie INTEGER,
                carga REAL,
                reps INTEGER,
                data DATE,
                FOREIGN KEY (exercicio_id) REFERENCES exercicios(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        ''')

        # Seed admin user with default password "admin123"
        cur.execute("SELECT * FROM usuarios WHERE nome = 'admin'")
        if not cur.fetchone():
            hashed = generate_password_hash('admin123')
            cur.execute("INSERT INTO usuarios (nome, senha, role) VALUES (?, ?, 'admin')", ('admin', hashed))

        db.commit()

# ---------------- Routes ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        senha = request.form['senha'].strip()
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM usuarios WHERE nome = ?", (nome,))
        user = cur.fetchone()
        if user and check_password_hash(user['senha'], senha):
            session['usuario_id'] = user['id']
            session['usuario_nome'] = user['nome']
            session['role'] = user['role']
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            elif user['role'] == 'coach':
                return redirect(url_for('painel_coach'))
            else:
                return redirect(url_for('index'))
        else:
            return render_template('login.html', erro="Usuário ou senha inválidos")
    return render_template('login.html')

@app.route('/index')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cur = db.cursor()
    usuario_id = session['usuario_id']
    cur.execute("SELECT id, nome FROM exercicios WHERE usuario_id = ?", (usuario_id,))
    exercicios = cur.fetchall()
    cur.execute("""
        SELECT data, nome, serie, carga, reps
        FROM series
        JOIN exercicios ON series.exercicio_id = exercicios.id
        WHERE series.usuario_id = ?
        ORDER BY data DESC
    """, (usuario_id,))
    historico = cur.fetchall()
    return render_template("index.html", usuario=session['usuario_nome'], exercicios=exercicios, series=historico)

@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html')

@app.route('/painel_coach')
def painel_coach():
    if 'role' not in session or session['role'] != 'coach':
        return redirect(url_for('login'))
    return "Painel do Coach em construção"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- Init ----------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
