from flask_login import UserMixin
import sqlite3
import bcrypt

conn = sqlite3.connect("users.db")  #Criando o DB de usuarios e inicializando um usuario admin
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS user_data
(user_id, pass_hash, name, email, auth, admin)''')
c.execute('''SELECT * from user_data WHERE user_id = ? ''',('admin',))
adm_user = c.fetchall()
if len(adm_user) == 0:
    adm_pwd = 'admin'
    adm_pwd = adm_pwd.encode('utf-8')
    c.execute('''INSERT INTO user_data VALUES (:user_id, :pass_hash, :name,:email, :auth, :admin)''',{
        'user_id': 'admin',
        'name': 'Admin',
        'email': None,
        'pass_hash': bcrypt.hashpw(adm_pwd, bcrypt.gensalt()),
        'auth': True,
        'admin': True
    })
conn.commit()
conn.close()


class User(UserMixin): # Classe de Usuario com suas devidas propriedades
    def __init__(self,admin,user_id,name,email,auth):
        self.admin=admin
        self.user_id=user_id
        self.name=name
        self.email=email
        self.auth=auth
    
    def get_id(self):
        return self.user_id
    
    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "admin": self.admin,
            "auth": self.auth
        }

class Users(): # Classe que tem como funcao fazer a checagem de existencia do usuario, checar se a senha esta correta e por fim retornar o usuario com a mensagem de login.
    def get_user_for_login(user_id,password):
        conn = sqlite3.connect("users.db")
        c=conn.cursor()
        c.execute('''SELECT admin,user_id,name,email,auth,pass_hash from user_data WHERE user_id = ? ''',(user_id,))
        users=c.fetchall()
        conn.commit()
        conn.close()
        if len(users) != 1:
            return None, "Usuário não encontrado!"
        user = users[0]
        hashed = user[5]
        if user[4] == False:
            return None, "Usuário não possui autorização! Contate seu admnistrador."
        if bcrypt.checkpw(password.encode('utf-8'),hashed) == True:
            return User(admin=user[0],user_id=user[1],name=user[2],email=user[3],auth=user[4]), "Logado!"
        else:
            return None, "Senha Incorreta!"