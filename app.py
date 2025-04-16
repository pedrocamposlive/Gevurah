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
            CREATE TABLE IF NOT EXISTS treinos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                titulo TEXT,
                descricao TEXT,
                data DATE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            );
        ''')

        # Admin padrão
        cur.execute("SELECT * FROM usuarios WHERE nome = 'admin'")
        if not cur.fetchone():
            cur.execute("INSERT INTO usuarios (nome, senha, role) VALUES (?, ?, 'admin')",
                        ('admin', generate_password_hash('admin123')))

        # Coach de teste
        cur.execute("SELECT * FROM usuarios WHERE nome = 'coachbeta'")
        if not cur.fetchone():
            cur.execute("INSERT INTO usuarios (nome, senha, role) VALUES (?, ?, 'coach')",
                        ('coachbeta', generate_password_hash('coach123')))

        # Aluno de teste
        cur.execute("SELECT * FROM usuarios WHERE nome = 'alunobeta'")
        if not cur.fetchone():
            # Buscar ID do coach
            cur.execute("SELECT id FROM usuarios WHERE nome = 'coachbeta'")
            coach_id = cur.fetchone()['id']
            cur.execute("INSERT INTO usuarios (nome, senha, role, coach_id) VALUES (?, ?, 'aluno', ?)",
                        ('alunobeta', generate_password_hash('aluno123'), coach_id))

        db.commit()

# ---------------- Rotas ----------------
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
                return redirect('/admin')
            elif user['role'] == 'coach':
                return redirect('/coach')
            else:
                return redirect('/index')
        else:
            return render_template('login.html', erro="Usuário ou senha inválidos")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/index')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    usuario_id = session['usuario_id']
    db = get_db()
    cur = db.cursor()

    # Treinos do aluno
    cur.execute("SELECT * FROM treinos WHERE usuario_id = ? ORDER BY data DESC", (usuario_id,))
    treinos = cur.fetchall()

    return render_template("index.html", usuario=session['usuario_nome'], treinos=treinos)

@app.route('/coach')
def coach_dashboard():
    if session.get('role') != 'coach':
        return redirect('/')
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM usuarios WHERE coach_id = ?", (session['usuario_id'],))
    alunos = cur.fetchall()
    return render_template("coach.html", coach=session['usuario_nome'], alunos=alunos)

@app.route('/criar_treino/<int:aluno_id>', methods=['GET', 'POST'])
def criar_treino(aluno_id):
    if session.get('role') != 'coach':
        return redirect('/')
    db = get_db()
    cur = db.cursor()
    # Valida se o aluno pertence ao coach
    cur.execute("SELECT * FROM usuarios WHERE id = ? AND coach_id = ?", (aluno_id, session['usuario_id']))
    aluno = cur.fetchone()
    if not aluno:
        return "Acesso negado"
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_hoje = date.today()
        cur.execute("INSERT INTO treinos (usuario_id, titulo, descricao, data) VALUES (?, ?, ?, ?)",
                    (aluno_id, titulo, descricao, data_hoje))
        db.commit()
        return redirect('/coach')
    return render_template("form_treino.html", aluno=aluno)

# ---------------- Init ----------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
