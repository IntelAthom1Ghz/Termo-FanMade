import sqlite3 
import os

def init_db():
    os.makedirs('app', exist_ok= True)
    with sqlite3.connect('app/usuarios.db') as conn:
        cursor = conn.cursor()
        
        cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            pontos TEXT)
            """)
        
        
        cursor.execute(""" CREATE TABLE IF NOT EXISTS ranking(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tentativas TEXT)
            """)
        
        

        conn.commit()
        
def deletar_usuario(email):
    try:
        with sqlite3.connect('app/usuarios.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM usuarios WHERE email = ?', (email,))
            conn.commit()
            print(f'Usuário com email {email} foi deletado do banco de dados com sucesso!')
    except sqlite3.IntegrityError as e:
        print(f'Erro de integridade: {e}')
        


