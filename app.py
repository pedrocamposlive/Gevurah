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
                aluno_id INTEGER,
                descricao TEXT NOT NULL,
                data DATE DEFAULT CURRENT_DATE,
                FOREIGN KEY (aluno_id) REFERENCES usuarios(id)
            );
        ''')

        # Seed admin user
        cur.execute("SELECT * FROM usuarios WHERE nome = 'admin'")
        if not cur.fetchone():
            hashed = generate_password_hash('admin123')
            cur.execute("INSERT INTO usuarios (nome, senha, role) VALUES (?, ?, 'admin')", ('admin', hashed))

        # Seed coach
        cur.execute("SELECT * FROM usuarios WHERE nome = 'coachbeta'")
        if not cur.fetchone():
            hashed = generate_password_hash('coach123')
            cur.execute("INSERT INTO usuarios (nome, senha, role) VALUES (?, ?, 'coach')", ('coachbeta', hashed))
            coach_id = cur.lastrowid

            hashed_aluno = generate_password_hash('aluno123')
            cur.execute("INSERT INTO usuarios (nome, senha, role, coach_id) VALUES (?, ?, 'user', ?)", ('alunobeta', hashed_aluno, coach_id))
            aluno_id = cur.lastrowid

            # Exemplo de treino baseado na imagem
            treino_texto = '''
B - ( Costas e bíceps )

- Remada curvada c/ barra peg supinada smith 5 x20/15/12/10/8 (c/ progressão de carga a cada série)
- Remada cavalinho 4x15 rep (carga máxima)
- Remada unilateral máquina pegada neutra 4x15/12/12/10
- Remada baixa c/ triângulo 4x15 rep
- Crucifixo inverso c/ halteres 4x15 rep (carga máxima)
- Rosca scott c/ barra W + conjugado c/ martelo alternada 4x12 rep
- Rosca alternada sentada 3x15 rep
- Abs supra + abs infra 3x15 rep

Obs: descanso de 1 min entre as séries'''

            cur.execute("INSERT INTO treinos (aluno_id, descricao) VALUES (?, ?)", (aluno_id, treino_texto))

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
            if user['role'] == 'admin' or user['role'] == 'coach':
                return redirect(url_for('admin'))
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

    # Verificar treino do usuário
    cur.execute("SELECT * FROM treinos WHERE aluno_id = ? ORDER BY data DESC LIMIT 1", (usuario_id,))
    treino = cur.fetchone()

    return render_template("index.html", usuario=session['usuario_nome'], treino=treino)

@app.route('/admin')
def admin():
    if 'role' not in session or session['role'] not in ['admin', 'coach']:
        return redirect(url_for('login'))

    db = get_db()
    cur = db.cursor()
    usuario_id = session['usuario_id']
    role = session['role']

    if role == 'admin':
        cur.execute("SELECT u.id, u.nome, u.role, c.nome as coach_nome FROM usuarios u LEFT JOIN usuarios c ON u.coach_id = c.id ORDER BY u.id")
    else:
        cur.execute("SELECT u.id, u.nome, u.role, c.nome as coach_nome FROM usuarios u LEFT JOIN usuarios c ON u.coach_id = c.id WHERE u.coach_id = ? ORDER BY u.id", (usuario_id,))

    usuarios = cur.fetchall()
    return render_template('admin.html', usuarios=usuarios)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------- Init ----------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
