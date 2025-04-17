# Iniciando migração para Flask AdminLTE dashboard base.
# Este é o ponto inicial do novo app baseado na estrutura sugerida.

from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# Banco de dados SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'adminlte.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='aluno')
    coach_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    coach = db.relationship('Usuario', remote_side=[id])

class Exercicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))

class Serie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicio.id'))
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    serie = db.Column(db.Integer)
    carga = db.Column(db.Float)
    reps = db.Column(db.Integer)
    data = db.Column(db.String(20))

# Rotas principais
@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome = request.form['nome']
        senha = request.form['senha']
        user = Usuario.query.filter_by(nome=nome).first()
        if user and check_password_hash(user.senha, senha):
            session['user_id'] = user.id
            session['role'] = user.role
            session['nome'] = user.nome
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'coach':
                return redirect(url_for('coach_dashboard'))
            else:
                return redirect(url_for('aluno_dashboard'))
        flash('Usuário ou senha incorretos')
    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/index.html')

@app.route('/coach')
def coach_dashboard():
    if session.get('role') != 'coach':
        return redirect(url_for('login'))
    return render_template('coach/index.html')

@app.route('/aluno')
def aluno_dashboard():
    if session.get('role') != 'aluno':
        return redirect(url_for('login'))
    return render_template('aluno/index.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Inicializa banco com dados
@app.before_first_request
def create_tables():
    db.create_all()
    if not Usuario.query.filter_by(nome='admin').first():
        db.session.add(Usuario(nome='admin', senha=generate_password_hash('admin123'), role='admin'))
        db.session.add(Usuario(nome='coachbeta', senha=generate_password_hash('coach123'), role='coach'))
        db.session.add(Usuario(nome='alunobeta', senha=generate_password_hash('aluno123'), role='aluno', coach_id=2))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
