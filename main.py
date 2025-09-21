from flask import Flask, make_response
from markupsafe import escape   
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask import url_for
from flask import redirect
from datetime import datetime
from flask_login import (current_user, LoginManager, login_user, logout_user, login_required)

import hashlib  

app = Flask(__name__)
## Configurando a ligação com o BD  = 'mysql://USUARIO:SENHA@SERVIDOR:PORTA/DATABASE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://testuser:toledo22@localhost/mydb'



#uso para retirar um warning
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  

db = SQLAlchemy(app)

app.secret_key = 'segredo_verenxovais'
login_manager = LoginManager()
login_manager.init_app(app) 
login_manager.login_view = 'login'  # Define a rota de login


# MODELS - CLASSES QUE REPRESENTAM AS TABELAS #
class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario = db.Column('id_usuario', db.Integer, primary_key=True)
    nome = db.Column('nome', db.String(200)) 
    login = db.Column('login', db.String(50))
    senha = db.Column('senha', db.String(256))  # Senha criptografada
    email = db.Column('email', db.String(150))
    fone = db.Column('fone', db.String(100))
    rua = db.Column('rua', db.String(256))
    numero = db.Column('numero', db.String(20))
    bairro = db.Column('bairro', db.String(80))
    cidade = db.Column('cidade', db.String(100))
    estado = db.Column('estado', db.String(20))
    cep = db.Column('cep', db.String(100))
  
    def __init__(self, nome, login, senha, email, fone, rua, numero, bairro, cidade, estado, cep):
        self.nome = nome
        self.login = login
        self.senha = senha
        self.email = email
        self.fone = fone
        self.rua = rua
        self.numero = numero
        self.bairro = bairro
        self.cidade = cidade
        self.estado = estado
        self.cep = cep

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True 

    def is_anonymous(self):
        return False

    def get_id(self):   
        return str(self.id_usuario) 
    
class Anuncio(db.Model):
    __tablename__ = "anuncio"
    id_anuncio = db.Column('id_anuncio', db.Integer, primary_key=True)
    nome = db.Column('nome', db.String(200))  # Nome do Anúncio
    descricao = db.Column('descricao', db.String(500))  # Descrição do Anúncio  
    data = db.Column('data', db.DateTime, nullable=False)  # Data do Anúncio
    quantidade = db.Column('quantidade', db.Integer)   # Quantidade do Anúncio
    valor = db.Column('valor', db.Float) # Valor do Anúncio
    situacao = db.Column('situacao', db.String(45))  # Situação do Anúncio (Ativo, Vendido, Cancelado)
    id_us_prop_anuncio = db.Column('id_us_prop_anuncio', db.Integer, db.ForeignKey('usuario.id_usuario'))
    id_cat = db.Column('id_categoria', db.ForeignKey('categoria.id_categoria'))   
    
    def __init__(self, nome, descricao, data, quantidade, valor, situacao, id_us_prop_anuncio, id_cat):
         self.nome = nome
         self.descricao = descricao
         self.data = data
         self.quantidade = quantidade
         self.valor = valor
         self.situacao = situacao
         self.id_us_prop_anuncio = id_us_prop_anuncio
         self.id_cat = id_cat   

class Perg_resp(db.Model):
    __tablename__ = "perg_resp"
    id_perg_resp = db.Column('id_perg_resp', db.Integer, primary_key=True)
    tipo = db.Column('tipo', db.String(45))  # Pergunta ou Resposta
    data = db.Column('data', db.DateTime, nullable=False)
    descricao = db.Column('descricao', db.String(500))
    id_anuncio = db.Column('id_anuncio', db.ForeignKey('anuncio.id_anuncio'))
    id_usuario = db.Column('id_usuario', db.ForeignKey('usuario.id_usuario'))

    anuncio= db.relationship('Anuncio', backref='perguntas_respostas')  
    usuario = db.relationship('Usuario', backref='perguntas_respostas') 
 
    def __init__(self, tipo, data, descricao, id_anuncio, id_usuario):  
        self.tipo = tipo
        self.data = data
        self.descricao = descricao
        self.id_anuncio = id_anuncio
        self.id_usuario = id_usuario

class Categoria(db.Model):
    __tablename__ = "categoria"
    id_categoria = db.Column('id_categoria', db.Integer, primary_key=True)
    descricao = db.Column('descricao', db.String(500))
    
    def __init__(self, descricao):
        self.descricao = descricao

class Anunc_favor(db.Model):   
    __tablename__ = "anunc_favor"
    id_sequencia = db.Column('id_sequencia', db.Integer, primary_key=True)
    id_anuncio_favorito = db.Column('id_anuncio_favorito', db.Integer, nullable=False)
    id_usuario = db.Column('id_usuario', db.ForeignKey('usuario.id_usuario'))

    def __init__(self, data, id_anuncio_favorito, id_usuario):
        self.id_anuncio = id_anuncio
        self.id_usuario = id_usuario   

class Compra(db.Model):
    __tablename__ = "compra"
    id_transacao = db.Column('id_transacao', db.Integer, primary_key=True)
    tipo = db.Column('tipo', db.String(45))  # Compra ou Venda
    data = db.Column('data', db.DateTime, nullable=False)
    valor = db.Column('valor', db.Float)
    nota_fiscal = db.Column('nota_fiscal', db.String(500))
    id_usuario = db.Column('id_usuario', db.ForeignKey('usuario.id_usuario'))
    id_anuncio = db.Column('id_anuncio', db.ForeignKey('anuncio.id_anuncio'))

    def __init__(self, tipo, data, valor, nota_fiscal, id_anuncio, id_usuario): 
        self.tipo = tipo
        self.data = data
        self.valor = valor
        self.nota_fiscal = nota_fiscal
        self.id_anuncio = id_anuncio
        self.id_usuario = id_usuario  
       

####################### ROTAS #######################
### Rota para tratamento de erro 404 - Página não encontrada
@app.errorhandler(404)
def paginanaoencontrada(error):
    return render_template('pagnaoencontrada.html'), 404    

#### Configuração do carregamento do usuário para o Flask-Login
@login_manager.user_loader
def load_user(id_usuario):
    return Usuario.query.get(int(id_usuario))      

### ROTA PARA A PÁGINA INICIAL E LISTAGEM DE ANÚNCIOS ATIVOS
@app.route("/")
@login_required  # Garante que o usuário esteja logado para acessar a página inicial
def index():
    anuncios_ativos = Anuncio.query.filter_by(situacao="Ativo").all()
    return render_template('index.html', anuncios=anuncios_ativos)

### ROTA PARA LOGIN E LOGOUT
@app.route("/login", methods=['GET', 'POST'])
def login():    
    if request.method == 'POST':
        login = request.form.get('login')
        senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        user = Usuario.query.filter_by(login=login, senha=senha).first()
        
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            return "Login ou senha inválidos", 404  
            redirect(url_for('login'))
    return render_template('login.html', titulo="Login")

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))   

#### USUARIOS - ROTAS ####
@app.route("/cad/usuarios")
@login_required  
def cadusuario():
    return render_template('usuarios.html', usuarios = Usuario.query.all(), titulo="Usuarios")

@app.route("/usuario/criar", methods=['POST'])
def criarusuario():
    # Criptografando a senha antes de armazenar
    hash = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
    usuario = Usuario(
        request.form.get('nome'),
        request.form.get('login'),
        hash,
        request.form.get('email'),
        request.form.get('fone'),
        request.form.get('rua'),
        request.form.get('numero'),
        request.form.get('bairro'),
        request.form.get('cidade'),
        request.form.get('estado'),
        request.form.get('cep')
    )
    db.session.add(usuario)
    db.session.commit() 
    return redirect(url_for('cadusuario'))

@app.route("/usuario/detalhar/<int:id_usuario>")
def detalharusuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)
    if usuario:
        return usuario.nome + "<br>" + \
               usuario.login + "<br>" + \
               usuario.email + "<br>" + \
               usuario.fone + "<br>" + \
               usuario.rua + "<br>" + \
               usuario.numero + "<br>" + \
               usuario.bairro + "<br>" + \
               usuario.cidade + "<br>" + \
               usuario.estado + "<br>" + \
               usuario.cep      
    else:
        return "Usuário não encontrado", 404

@app.route("/usuario/editar/<int:id_usuario>", methods=['GET', 'POST'])
def editarusuario(id_usuario):  
    usuario = Usuario.query.get(id_usuario)
    if request.method == 'POST':
        usuario.nome = request.form.get('nome')
        usuario.login = request.form.get('login')
        usuario.senha = hashlib.sha512(str(request.form.get('senha')).encode("utf-8")).hexdigest()
        usuario.email = request.form.get('email')   
        usuario.fone = request.form.get('fone')
        usuario.rua = request.form.get('rua')
        usuario.numero = request.form.get('numero')
        usuario.bairro = request.form.get('bairro')
        usuario.cidade = request.form.get('cidade')
        usuario.estado = request.form.get('estado')
        usuario.cep = request.form.get('cep')
        db.session.add(usuario)
        db.session.commit()
        return redirect(url_for('cadusuario'))
    return render_template('edit_usuario.html', usuario = usuario, titulo="Usuarios")          

@app.route("/usuario/excluir/<int:id_usuario>", methods=['GET', 'POST'])
def excluirusuario(id_usuario):
    usuario = Usuario.query.get_or_404(id_usuario)  # retorna 404 automaticamente se não existir

    if request.method == 'POST':
        if request.form.get('confirmar') == 'sim':
            db.session.delete(usuario)
            db.session.commit()
        return redirect(url_for('cadusuario'))

    # GET → mostra a página de confirmação
    return render_template(
        'confirmarexclusao.html',  # sem acento no nome do arquivo
        usuario=usuario
    )

         
####################### CATEGORIAS - ROTAS #######################
@app.route("/cad/categoria")
@login_required
def cadcategoria():
    return render_template('categorias.html',categorias = Categoria.query.all(), titulo="Categorias")

@app.route("/categoria/criar", methods=['POST'])
def criarcategoria():
    categoria = Categoria(
        request.form.get('descricao')
    )
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('cadcategoria'))

@app.route("/categoria/detalhar/<int:id_categoria>")
def detalharcategoria(id_categoria):
    categoria = Categoria.query.get(id_categoria)
    if categoria:
        return categoria.descricao
    else:
        return "Categoria não encontrada", 404

@app.route("/categoria/editar/<int:id_categoria>", methods=['GET', 'POST'])
def editarcategoria(id_categoria):
    categoria = Categoria.query.get(id_categoria)
    if request.method == 'POST':
        categoria.descricao = request.form.get('descricao')
        db.session.add(categoria)
        db.session.commit()
        return redirect(url_for('cadcategoria'))    
    return render_template('edit_categoria.html', categoria = categoria, titulo="Categorias")   

@app.route("/categoria/excluir/<int:id_categoria>", methods=['GET', 'POST'])
def excluircategoria(id_categoria):     
    categoria = Categoria.query.get(id_categoria)
    if not categoria:
        return "Categoria não encontrada", 404
    
    if request.method == 'POST':
        if request.form.get('confirmar') == 'sim':
            db.session.delete(categoria)
            db.session.commit()
            return redirect(url_for('cadcategoria'))   
        else:
            return "Categoria não encontrada", 404
    return render_template('confirmarexclusão.html',url_cancelar ='cadcategoria')  

####################### ANUNCIOS - ROTAS #######################
@app.route("/cad/anuncio")
@login_required
def cadanuncio():
    return render_template('anuncios.html',
    anuncios=Anuncio.query.all(),
    usuarios=Usuario.query.all(),
    categorias=Categoria.query.all(),
    titulo="Anúncios" )

@app.route("/anuncio/criar", methods=['POST'])
def criaranuncio(): 
    data_str = request.form.get('data')  
    data = datetime.strptime(data_str, '%Y-%m-%d') if data_str else None

    valor_str = request.form.get('valor', '').replace(',', '.')
    valor = float(valor_str) if valor_str else 0.0

    quantidade_str = request.form.get('quantidade', '0')
    quantidade = int(quantidade_str) if quantidade_str.isdigit() else 0

    id_us_prop_anuncio = int(request.form.get('id_us_prop_anuncio'))
    id_cat = int(request.form.get('id_cat'))
    print(f"id_us_prop_anuncio: {id_us_prop_anuncio}, id_cat: {id_cat}")    

    anuncio = Anuncio(
        request.form.get('nome'),
        request.form.get('descricao'),
        data,
        quantidade,
        valor,
        request.form.get('situacao'),
        id_us_prop_anuncio,  
        id_cat          
    )
    db.session.add(anuncio)
    db.session.commit()
    return redirect(url_for('cadanuncio'))

@app.route("/detalharanuncio/<int:id_anuncio>")
def detalharanuncio(id_anuncio):
    anuncio = Anuncio.query.get(id_anuncio)
    mensagens = Perg_resp.query.filter_by(id_anuncio=id_anuncio).order_by(Perg_resp.data.desc()).all()

    # Usuário fixo para testes (ex: id 1) depois de implementar o login, substituir por get_usuario_logado()
    usuario_logado = Usuario.query.get(3)
        
    return render_template('detalharanuncio.html',
                            anuncio=anuncio,
                            mensagens=mensagens,
                            usuario_logado=usuario_logado,
                            titulo="Anúncios")  
    
@app.route("/anuncio/editar/<int:id_anuncio>", methods=['GET', 'POST'])
def editaranuncio(id_anuncio):
    anuncio = Anuncio.query.get(id_anuncio)
    if request.method == 'POST':
        anuncio.nome = request.form.get('nome')
        anuncio.descricao = request.form.get('descricao')
        anuncio.data = request.form.get('data')
        anuncio.quantidade = request.form.get('quantidade')
        anuncio.valor = request.form.get('valor')
        anuncio.situacao = request.form.get('situacao')
        anuncio.id_us_prop_anuncio = request.form.get('id_us_prop_anuncio')
        anuncio.id_cat = request.form.get('id_cat')
        db.session.add(anuncio)
        db.session.commit()
        return redirect(url_for('cadanuncio'))

    categorias = Categoria.query.all()
    
    return render_template('edit_anuncio.html',
                            anuncio = anuncio,
                            categorias=categorias,
                            titulo="Anúncios")

@app.route("/anuncio/excluir/<int:id_anuncio>", methods=['GET', 'POST'])
def excluiranuncio(id_anuncio):
    anuncio = Anuncio.query.get(id_anuncio)
    if not anuncio:
        return "Anúncio não encontrado", 404    

    if request.method == 'POST':
        if request.form.get('confirmar') == 'sim':
            db.session.delete(anuncio)
            db.session.commit()
            return redirect(url_for('cadanuncio'))
        else:
            return redirect(url_for('cadanuncio'))
    
    return render_template('confirmarexclusão.html', url_cancelar='cadanuncio')         

@app.route('/enviar_pergunta_resposta/<int:id_anuncio>', methods=['POST'])
def enviar_pergunta_resposta(id_anuncio):
    descricao = request.form['descricao']
    tipo = request.form['tipo']
    id_usuario = request.form['id_usuario']

    nova_mensagem = Perg_resp(
        descricao=descricao,
        tipo=tipo,
        data=datetime.now(),
        id_anuncio=id_anuncio,
        id_usuario=id_usuario
    )

    db.session.add(nova_mensagem)
    db.session.commit()

    return redirect(url_for('detalharanuncio', id_anuncio=id_anuncio))

if __name__ == "__main__":
    app.run(debug=True)


