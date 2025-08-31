from flask import Flask, make_response, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)
from datetime import datetime
import hashlib  

# Inicialização da aplicação Flask
app = Flask(__name__)
app.secret_key = 'Verenxovais2025'

# Configuração do Banco de Dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://usuario:senha@servidor:3306/verenxovais_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

# Extensões
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'acesso_login'

# Criando tabelas caso não existam
with app.app_context():
    db.create_all()

# ------------------ MODELOS ------------------
class Cliente(db.Model):
    __tablename__ = "clientes"
    id_cliente = db.Column('id_cliente', db.Integer, primary_key=True)
    nome_completo = db.Column('nome_completo', db.String(200))
    usuario_login = db.Column('usuario_login', db.String(50))
    senha_acesso = db.Column('senha_acesso', db.String(256))
    email_contato = db.Column('email_contato', db.String(150))
    telefone = db.Column('telefone', db.String(100))
    endereco_rua = db.Column('endereco_rua', db.String(256))
    endereco_numero = db.Column('endereco_numero', db.String(20))
    bairro_local = db.Column('bairro_local', db.String(80))
    cidade_local = db.Column('cidade_local', db.String(100))
    estado_local = db.Column('estado_local', db.String(20))
    cep_local = db.Column('cep_local', db.String(100))

    def get_id(self):
        return str(self.id_cliente)

class Produto(db.Model):
    __tablename__ = "produtos"
    id_produto = db.Column('id_produto', db.Integer, primary_key=True)
    nome_produto = db.Column('nome_produto', db.String(200))
    descricao_produto = db.Column('descricao_produto', db.String(500))
    data_cadastro = db.Column('data_cadastro', db.DateTime, nullable=False)
    estoque = db.Column('estoque', db.Integer)
    preco = db.Column('preco', db.Float)
    status_produto = db.Column('status_produto', db.String(45))
    id_cliente_dono = db.Column('id_cliente_dono', db.Integer, db.ForeignKey('clientes.id_cliente'))
    id_categoria = db.Column('id_categoria', db.ForeignKey('categorias.id_categoria'))

class CategoriaProduto(db.Model):
    __tablename__ = "categorias"
    id_categoria = db.Column('id_categoria', db.Integer, primary_key=True)
    nome_categoria = db.Column('nome_categoria', db.String(500))

# ------------------ ROTAS ------------------
@app.route("/")
@login_required
def pagina_inicial():
    produtos_ativos = Produto.query.filter_by(status_produto="Disponível").all()
    return render_template('index.html', produtos=produtos_ativos)

@app.route("/login", methods=['GET', 'POST'])
def acesso_login():
    if request.method == 'POST':
        usuario = request.form.get('usuario_login')
        senha = hashlib.sha512(str(request.form.get('senha_acesso')).encode("utf-8")).hexdigest()
        cliente = Cliente.query.filter_by(usuario_login=usuario, senha_acesso=senha).first()
        if cliente:
            login_user(cliente)
            return redirect(url_for('pagina_inicial'))
        else:
            return "Usuário ou senha inválidos", 401
    return render_template('login.html', titulo="Acesso Verenxovais")

@app.route("/logout")
def sair():
    logout_user()
    return redirect(url_for('acesso_login'))
