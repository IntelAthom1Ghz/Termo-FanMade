from flask import Blueprint, render_template, request, redirect,url_for, session, flash, g
import sqlite3
from estudos import bcrypt
from .utils import login_required, carregar_palavras
from .forms import LoginForm, CadastroForm, NovaSenhaForm, SenhaForm
import random
from flask_mail import Message
from . import mail
palavras = carregar_palavras()
views = Blueprint('views', __name__)

@views.route('/')
def index():
    return render_template('index.html')
def gerar_hash(senha):
    hash_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
    return hash_senha

def verificar_senha(senha_digitada, senha_hash):
    return bcrypt.check_password_hash(senha_hash, senha_digitada)


@views.route('/login', methods =['POST','GET'])
def login():
    form = LoginForm()
    erro = None
    
    if form.validate_on_submit():
        email = form.email.data
        senha = form.senha.data 
        
        with sqlite3.connect('app/usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT senha, nome FROM usuarios WHERE email = ?', (email,))
            row = cursor.fetchone()
            
            if row and verificar_senha(senha, row[0]):
                session['usuario'] = row[1] #salva a sessão e expira depois de 15 min,  tendo que logar dnv dps desse tempo
                session.permanent = True
                return redirect(url_for('views.dashboard'))
            else:
                erro = 'Email ou senha incorretos'
    return render_template('login.html', erro = erro, form = form)     
@views.route('/dashboard', methods =['POST', 'GET'])
@login_required
def dashboard():
    return render_template('index.html', nome=session['usuario'])

@views.route('/cadastro', methods =['POST', 'GET'])
def cadastro():
    form =CadastroForm()
    erro = None
    
    if form.validate_on_submit():
        nome = form.nome.data
        email = form.email.data
        senha = form.senha.data
        senha_hash = gerar_hash(senha)
        with sqlite3.connect('app/usuarios.db') as conn:
            cursor = conn.cursor()
            #verificacao se ja existe esse email no banco
            cursor.execute('SELECT id FROM usuarios WHERE email = ?', (email,))
            if cursor.fetchone():
                erro = 'Email já cadastrado em nosso site'
                return render_template('cadastro.html', erro = erro, form = form)
                
            cursor.execute('INSERT INTO usuarios (nome, email, senha, pontos) VALUES (?,?,?,?)', (nome, email, senha_hash, '0'))
            conn.commit()
        
        
        return redirect(url_for('views.login'))
    return render_template('cadastro.html', form = form, erro = erro)


@views.route('/nova_senha', methods = ['POST', 'GET'])
def nova_senha():
    form = NovaSenhaForm()
    erro = None
    if form.validate_on_submit():
        email = form.email.data
        with sqlite3.connect('app/usuarios.db') as conn:
            cursor = conn.cursor()
            
            cursor.execute ('SELECT * FROM usuarios WHERe email = ?', (email,))
            usuario = cursor.fetchone()
            if usuario:
                link_reset = url_for('views.criar_nova_senha', email = (email), _external = True)
                msg = Message('Redefinição de senha', recipients = [email])
                msg.body = f'Clique no link para redefinir sua senha: \n {link_reset}'
                mail.send(msg)
                
                flash('Instruções enviadas para seu e-mail', 'success')
                return redirect(url_for('views.login'))
            else:
                erro = 'Email não encontrado'
    return render_template('nova_senha.html', form = form, erro = erro)    
    
@views.route('/nova_senha<email>', methods =['POST','GET'])
def criar_nova_senha(email):
    form = SenhaForm()
    
    with sqlite3.connect('app/usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario = cursor.fetchone()
            
    if not usuario:
        flash('Link inválido ou usuário não existe em nossa database', 'error')
        return redirect(url_for('nova_senha.html'))
    
    if form.validate_on_submit():
        nova_senha = form.senha.data
        senha_hash = gerar_hash(nova_senha)
        
        
        with sqlite3.connect('app/usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE usuarios SET senha = ? WHERE email = ?', (senha_hash, email))
            conn.commit()
            
            flash('Senha atualizada com sucesso!','success')
            return redirect(url_for('views.login'))
    
    return render_template('criar_nova_senha.html', email = email, form = form)
       
    

@views.route('/ranking', methods =['POST', 'GET'])
@login_required 
def ranking():
    with sqlite3.connect('app/usuarios.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nome, tentativas FROM ranking ORDER BY tentativas ASC LIMIT 10')
        jogadores = cursor.fetchall()
        return render_template('ranking.html', jogadores =jogadores)
    

def limpar_sessao_termo():
    session.pop('palavra_secreta', None)
    session.pop('tentativas_restantes', None)
    session.pop('tentativas_realizadas', None)

def avaliar_tentativa(palpite, palavra_secreta):
    resultado = [('', 'errada')] * 5  # inicializa
    palavra_lista = list(palavra_secreta)
    palpite_lista = list(palpite)
    
    resultado = [('', None)] * 5
    resultado = []
    
    # Primeiro passo: letras certas na posição certa
    for i in range(5):
        if palpite_lista[i] == palavra_lista[i]:
            resultado.append((palpite_lista[i], 'certa'))
            palavra_lista[i] = None
            palpite_lista[i] = None
        else:
            resultado.append((None, None))
    
    # Segundo passo: letras certas na posição errada (quase) e erradas
    for i in range(5):
        if palpite_lista[i] is not None:
            if palpite_lista[i] in palavra_lista:
                resultado[i] = (palpite_lista[i], 'quase')
                palavra_lista[palavra_lista.index(palpite_lista[i])] = None
            else:
                resultado[i] = (palpite_lista[i], 'errada')
    return resultado


@views.route('/termo', methods=['POST', 'GET'])
@login_required
def termo():
    if 'palavra_secreta' not in session:
        session['palavra_secreta'] = random.choice(palavras)
        session['tentativas_restantes'] = 6
        session['tentativas_realizadas'] = []

    palavra_secreta = session['palavra_secreta']
    tentativas_restantes = session['tentativas_restantes']
    tentativas_realizadas = session.get('tentativas_realizadas', [])
    mensagem = None

    if request.method == 'POST':
        palpite = request.form.get('palpite', '').lower()

        if len(palpite) != 5 or not palpite.isalpha():
            mensagem = 'Digite uma palavra com 5 letras.'
        else:
            resultado = avaliar_tentativa(palpite, palavra_secreta)
            tentativas_realizadas.append(resultado)
            session['tentativas_realizadas'] = tentativas_realizadas

            if palpite == palavra_secreta:
                # Salvar no banco ao vencer
                nome = session.get('usuario')
                if nome:
                    try:
                        with sqlite3.connect('app/usuarios.db') as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                'INSERT INTO ranking (nome, tentativas) VALUES (?, ?)',
                                (nome, len(tentativas_realizadas))
                            )
                            conn.commit()
                    except sqlite3.Error as e:
                        flash(f'Erro ao salvar no ranking: {e}', 'error')
                else:
                    flash('Usuário não identificado na sessão.', 'error')

                flash(f'Parabéns! Você adivinhou a palavra: {palavra_secreta}', 'success')
                limpar_sessao_termo()
                return redirect(url_for('views.termo'))

            session['tentativas_restantes'] = tentativas_restantes - 1
            tentativas_restantes = session['tentativas_restantes']

            if tentativas_restantes <= 0:
                flash(f'Você perdeu! A palavra era: {palavra_secreta}', 'danger')
                limpar_sessao_termo()
                return redirect(url_for('views.termo'))

    return render_template(
        'termo.html',
        tentativas_realizadas=tentativas_realizadas,
        tentativas_restantes=tentativas_restantes,
        mensagem=mensagem,
        nome=session['usuario']
    )

    
@views.route('/logout', methods ={'POST', 'GET'})
@login_required
def logout():
    session.pop('usuario', None)
    return redirect(url_for('views.login'))

                
                
                
    
    

    


        
        
    
   
