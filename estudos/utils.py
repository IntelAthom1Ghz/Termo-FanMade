from functools import wraps
from flask import session, redirect, url_for, flash
from pathlib import Path

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash("Você precisa estar logado para acessar esta página.", "warning")
            return redirect(url_for('views.login'))  # redireciona para a rota de login
        return f(*args, **kwargs)
    return decorated_function

def carregar_palavras(caminho = 'C:/Users/otavio/Documents/ESTUDOS 03082025/guess game/estudos/data/palavras.txt'):
    arquivo = Path(caminho)
    if not arquivo.exists():
        raise FileNotFoundError(f'Arquivo {caminho} não encontrado.')
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        palavras = [linha.strip().lower() for linha in f if len(linha.strip()) == 5]
        return palavras

