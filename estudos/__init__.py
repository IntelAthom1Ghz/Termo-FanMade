from flask import Flask
from datetime import timedelta
from flask_bcrypt import Bcrypt
import os
from flask_mail import Mail, Message
mail = Mail()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    
    app.secret_key = os.environ.get('SECRET_KEY', 'chave_padrao_insegura')
    
    app.permanent_session_lifetime = timedelta(minutes=15)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True #https
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    #dando init no banco de dados sql3lite
    from .database import init_db
    init_db()
    #iniciando o bcrypt 
    
    bcrypt.init_app(app)
    #regustrando as rotas
    from .views import views
    app.register_blueprint(views)
    
    app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='lojadagrazisite@gmail.com',
    MAIL_PASSWORD='dxfpyzqsfmmfjrnl',
    MAIL_DEFAULT_SENDER='lojadagrazisite@gmail.com'
)
    mail.init_app(app)
    
    
    
    return app
    