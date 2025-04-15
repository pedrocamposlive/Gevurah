from flask import Flask, render_template, request, redirect, url_for, session, g
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

        # Seed admin
        cur.execute("""
            INSERT OR IGNORE INTO usuarios (nome, role)
            VALUES ('admin', 'admin')
        """)

        db.commit()

# ---------------- Routes ----------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome'].strip()
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT id, role FROM usuarios WHERE nome = ?", (nome,))
        user = cur.fetchone()
        if not user:
            cur.execute("INSERT INTO usuarios (nome) VALUES (?)", (nome,))
            db.commit()
            cur.execute("SELECT id, role FROM usuarios WHERE nome = ?", (nome,))
            user = cur.fetchone()
        session['usuario_id'] = user['id']
        session['usuario_nome'] = nome
        session['role'] = user['role']
        return redirect(url_for('index'))
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
    if 'role' not in session:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    filtro = request.args.get('filtro', 'todos')
    usuario_id = session['usuario_id']
    role = session['role']

    cur.execute("SELECT id, nome FROM usuarios WHERE role = 'coach'")
    coaches = cur.fetchall()

    if role == 'admin':
        if filtro != 'todos':
            cur.execute("""
                SELECT u.id, u.nome, u.role, c.nome as coach_nome
                FROM usuarios u
                LEFT JOIN usuarios c ON u.coach_id = c.id
                WHERE u.role = ?
                ORDER BY u.id
            """, (filtro,))
        else:
            cur.execute("""
                SELECT u.id, u.nome, u.role, c.nome as coach_nome
                FROM usuarios u
                LEFT JOIN usuarios c ON u.coach_id = c.id
                ORDER BY u.id
            """)
    elif role == 'coach':
        cur.execute("""
            SELECT u.id, u.nome, u.role, c.nome as coach_nome
            FROM usuarios u
            LEFT JOIN usuarios c ON u.coach_id = c.id
            WHERE u.coach_id = ?
            ORDER BY u.id
        """, (usuario_id,))
    else:
        return redirect(url_for('index'))

    usuarios = cur.fetchall()
    return render_template('admin.html', usuarios=usuarios, filtro=filtro, coaches=coaches)

@app.route('/criar_usuario', methods=['POST'])
def criar_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))

    nome = request.form['nome'].strip()
    role = request.form['role']
    coach_id = request.form.get('coach_id') or None

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO usuarios (nome, role, coach_id)
        VALUES (?, ?, ?)
    """, (nome, role, coach_id))
    db.commit()
    return redirect(url_for('admin'))

@app.route('/alterar_usuario', methods=['POST'])
def alterar_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    user_id = request.form['id']
    novo_role = request.form['novo_role']
    db = get_db()
    cur = db.cursor()
    cur.execute("UPDATE usuarios SET role = ? WHERE id = ?", (novo_role, user_id))
    db.commit()
    return redirect(url_for('admin'))

@app.route('/excluir_usuario', methods=['POST'])
def excluir_usuario():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('index'))
    user_id = request.form['id']
    db = get_db()
    cur = db.cursor()
    cur.execute("DELETE FROM series WHERE usuario_id = ?", (user_id,))
    cur.execute("DELETE FROM exercicios WHERE usuario_id = ?", (user_id,))
    cur.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    db.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forcar_admin')
def forcar_admin():
    db = get_db()
    db.execute("UPDATE usuarios SET role = 'admin' WHERE nome = 'admin'")
    db.commit()
    return "Usuário 'admin' promovido!"

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
