from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    email = StringField('Digite seu email', validators=[Email(), DataRequired()])
    senha = PasswordField('Digite sua senha', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Entrar')

class CadastroForm(FlaskForm):
    nome = StringField('Digite seu nome completo', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Digite seu email', validators=[DataRequired(), Email()])
    senha = PasswordField('Digite sua senha', validators=[DataRequired(), Length(min=8)])
    confirmar_senha = PasswordField('Digite novamente sua senha', validators=[DataRequired(), EqualTo('senha', message='As senhas devem ser iguais')])
    enviar = SubmitField('Cadastrar')
    
class NovaSenhaForm(FlaskForm):
    email = StringField('Digite seu email', validators=[Email(), DataRequired()])
    confirmar_email = StringField('Digite novamente seu email', validators=[Email(), DataRequired(), EqualTo('email', message='Os campos email devem coincidir')])
    enviar = SubmitField('Enviar instruções')
    
class SenhaForm(FlaskForm):
    senha = PasswordField('Digite sua nova senha', validators=[DataRequired(), Length(min=8)])
    confirmar_senha = PasswordField('Digite novamente sua senha', validators=[DataRequired(), EqualTo('senha', message= 'As senhas devem ser iguais')])
    enviar = SubmitField('Efetuar troca de senha')
