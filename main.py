from functools import wraps
import os
import re
import time
from flask import Flask, abort, jsonify, request, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import sqlite3
import bcrypt
from user import User, Users
from datetime import date
import tags   # Import do arquivo tags acabou sendo utilizado somente para a criação do DB no sqlite, visto que a classe TAG acabou não sendo utilizada

app = Flask(__name__) # Iniciado o flask
app.secret_key = 'senha' #100% seguro. Confia!

login_manager = LoginManager()
login_manager.init_app(app)

linen_cat = {
    "Banho": ["Toalha de banho", "Toalha de rosto", "Tapete banheiro"],
    "Cama": ["Lençol", "Fronha", "Edredom"]
} # Criando dicionario de categorias de tags, numa versao final do app isso seria um DB onde o usuário poderia adicionar e remover categorias a vontade.

regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b' #Regex para checar se o endereço de email fornecido é correto.


def create_login_return(error_message=None, user=None): # Função para criar retorno JSON da soliticao
    resp = jsonify({"error_message": error_message, "user": user})
    resp.headers.add('Set-Cookie','cross-site-cookie=bar; SameSite=None;Secure') # Antes de utilizarmos tkinter tentamos brincar um pouco com React e Electron, e tivemos problemas para guardar os cookies da sessão no navegador.
    return resp                                                                  # Até que conseguimos criar um prototipo em electron mas tivemos problemas com a questao de leitura de porta serial e o tempo estava apertando, portanto foi abandonado.

def timeit(func): # Função não autoral, achada na internet com o único propósito de medir o tempo de execução de nossos requests. A utilização de htt://localhost no tkinter deixava o request lento e utilizando isso pudemos descobrir que se utilizar o endereco 127.0.0.1, ele processa muito mais rapido.
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Took {func.__name__}{args} {total_time:.4f} seconds')
        return result
    return timeit_wrapper


@login_manager.user_loader
@timeit
def load_user(user_id):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute(
        '''SELECT admin,user_id,name,email,auth from user_data WHERE user_id = ? ''', (user_id,))
    user = c.fetchall()
    conn.commit()
    conn.close()
    return User(*user[0])


@app.route("/login", methods=["POST"]) # Função de login
@timeit
def login():
    # print(request.json) 
    x = request.json  # Atribuindo o request em json recebido
    print(current_user)
    if current_user.is_authenticated: #Checar se o usuário já se encontran logado nesse dispostivo(Pode-ser criada diferentes sessões com a mesma conta)
        return create_login_return(error_message="Este usuário já está logado!")
    user, err = Users.get_user_for_login(x["user_id"], x["pwd"]) # Chamando a funcao da classe Users para checar se está tudo correto com os dados fornecidos
    if user is not None:
        login_user(user) #Funcao do flask_login, realizando login no usuario
        return create_login_return(user=user.to_dict(), error_message=err)
    else:
        return create_login_return(err)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    print(current_user)
    logout_user()   # Realização de Logout
    err = "Deslogado"
    return create_login_return(err)


@app.route("/current_user", methods=["POST"])
@login_required #Rota criada para retornar o atual usuário logado.
def current_user_req():
    return jsonify(current_user.to_dict())


@timeit
def create_signup_return(message, clear_all=False): #Funcao para criacao de retorno em JSON da funcao signup
    return jsonify({"message": message, "clear_all": clear_all})


@app.route("/signup", methods=["POST"]) #Funcao de criacao de conta
def signup():
    req = request.json
    user_id = req["user_id"]
    name = req["name"]
    email = req["email"]
    pwd = req["pwd"]
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''SELECT * from user_data WHERE user_id = ? ''', (user_id,))
    user = c.fetchall()
    conn.commit()
    conn.close()
    print(user)
    if len(user) != 0:
        return create_signup_return('Já existe um usuário com este nome')
    if len(user_id) < 5:
        return create_signup_return("O usuário precisa ter um mínimo de 5 carácteres.")
    if len(name) < 7:
        return create_signup_return("O nome precisa ter um mínimo de 7 carácteres")
    # if re.fullmatch(regex_email, email): #Por algum motivo nao funciona corretamente, nao deu tempo de ajeitar
    #     return create_signup_return("O email não é válido.")
    if len(pwd) < 8:
        return create_signup_return("A senha precisa ter um mínimo de 8 carácteres.")
    bpassword = pwd.encode('utf-8')
    hashed = bcrypt.hashpw(bpassword, bcrypt.gensalt()) # transformando a senha em hash para n salvar a senha direto no DB(não é seguro!)
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''INSERT INTO user_data VALUES (:user_id, :pass_hash, :name,:email, :auth, :admin)''', {
        'user_id': user_id, #id
        'name': name, #nome
        'email': email, #email
        'pass_hash': hashed, #senha hashed
        'auth': True, # se o usuario tem autorizacao pra login
        'admin': False # se o usuario é adm
    })
    conn.commit()
    conn.close()
    return create_signup_return("Conta Criada!", True)

@app.route("/check_tags", methods=["POST"]) # Funcao que checa se as tags lidas estão registradas no DB ou não
@login_required
def check_tags():
    x = request.json
    registered = []
    non_registered = []
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    for tag_id in x["tags"]:
        c.execute('''SELECT * from linen WHERE tag_id = ? ''', (tag_id,))
        tag = c.fetchall()
        if len(tag) != 0:
            registered.append(tag)
        else:
            non_registered.append(tag_id)
    conn.commit()
    conn.close()
    body = {
        "registered": registered,
        "non_registered": non_registered
    }
    return jsonify(body) 

@app.route("/reg_tags", methods=["POST"]) # Registrando as tags no DB e atualizando o log de eventos
@login_required
def reg_tags():
    x = request.json
    today = date.today()
    data = today.strftime("%d/%m/%Y")
    tag_list = x["tag_list"]
    aquisition_date = x["aquisition_date"]
    sub_category = x["category"]
    supplier = x["supplier"]
    clean = x["clean"]
    damage = x["damage"]
    status = x["status"]
    staff_name = current_user.name
    if sub_category in linen_cat["Banho"]:
        category = "Banho"
    else:
        category = "Cama"
    conn = sqlite3.connect("items.db")
    try:
        c = conn.cursor()
        for tag_id in tag_list:
            c.execute('''INSERT INTO linen VALUES (:tag_id, :aquisition_date, :category, :sub_category, :supplier, :clean, :damage, :status, :staff_name)''',{ # DB das tags
                'tag_id': tag_id, #id
                'aquisition_date': aquisition_date, #data de aquisicao
                'category': category, # categoria (Banho, Cama,etc)
                'sub_category': sub_category, #subcategoria (Toalha de Banho, edredom etc...)
                'supplier': supplier, #fornecedor
                'clean': clean, # se esta limpa ou nao
                'damage': damage, # danificada ou nao
                'status': status, # se o produto esta ativo para uso no hotel
                'staff_name': staff_name #nome do funcionario que registrou este produto
            })
            c.execute('''INSERT INTO log VALUES (:tag_id, :event_type, :date, :staff_name )''',{ # Log de Eventos
                "tag_id": tag_id, # id
                "event_type": "Registro", #no caso da funcao de registro so pode ser registro
                "date": data, #data de registro
                "staff_name": staff_name #nome do funcionario que registrou
            })
        conn.commit()
        conn.close()
        return {
            "message": "Registrado"
        }
    except:
        return {
            "message": "Erro"
        }
        

@app.route("/total_tags", methods = ["GET"]) # Funcao que retorna as estatisticas de tags para poder preencher o dashboard
@login_required
def total_tags():
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    c.execute('''SELECT * FROM linen''')
    total_tags = len(c.fetchall())
    c.execute('''SELECT * FROM linen WHERE NOT(status)''')
    discarded_tags = len(c.fetchall())
    c.execute('''SELECT * FROM linen WHERE NOT(clean) AND (status)''')
    dirty_tags = len(c.fetchall())
    c.execute('''SELECT * FROM linen WHERE (clean) AND (status)''')
    available_tags = len(c.fetchall())
    c.execute(''' SELECT * FROM linen WHERE (category = "Banho") ''')
    bath_items = len(c.fetchall())

    bath_items_subcat = {}
    for subcat in linen_cat["Banho"]:
        c.execute(''' SELECT * FROM linen WHERE (sub_category = ?)''', (subcat,))
        count = len(c.fetchall())
        bath_items_subcat[subcat] = count

    c.execute(''' SELECT * FROM linen WHERE (category = "Cama") ''')
    bed_items = len(c.fetchall())
    bed_items_subcat = {}
    for subcat in linen_cat["Cama"]:
        c.execute(''' SELECT * from linen WHERE (sub_category = ?)''', (subcat,))
        count = len(c.fetchall())
        bed_items_subcat[subcat] = count
            

    conn.commit()
    conn.close()
    data = {
        'total': total_tags,
        'discarded': discarded_tags,
        'dirty': dirty_tags,
        'available': available_tags,
        'bath': bath_items,
        'bed': bed_items,
        'bath_items': bath_items_subcat,
        'bed_items': bed_items_subcat 
    }
    return data

@app.route("/get_tags", methods = ["GET"]) # funcao para retornar todas as tags para preencher o inventario
@login_required
def get_tags():
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    c.execute('''SELECT * FROM linen''')
    tags = c.fetchall()
    conn.commit()
    conn.close()
    return jsonify(tags)

@app.route("/get_log", methods=["GET"]) # funcao para retornar o log de eventos para preencher o mesmo na interface
@login_required
def get_log():
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    c.execute('''SELECT * FROM log''')
    logs = c.fetchall()
    conn.commit()
    conn.close()
    return jsonify(logs)

@app.route("/change_tags", methods = ["POST"]) # funcao para poder alterar dados das tags e registrar esses eventos
@login_required
def change_tags():
    x = request.json
    tag_id = x["tag"]
    event = x["event"]
    today = date.today()
    staff_name = current_user.name
    data = today.strftime("%d/%m/%Y")
    conn = sqlite3.connect("items.db")
    c = conn.cursor()
    if event == "Limpa":
        c.execute('''UPDATE linen SET clean = 1 WHERE (tag_id = ?)''', (tag_id,))     
    elif event == "Suja":
        c.execute('''UPDATE linen SET clean = 0 WHERE (tag_id = ?)''', (tag_id,))
    elif event == "Ativa":
        c.execute('''UPDATE linen SET status = 1 WHERE (tag_id = ?)''', (tag_id,))
    elif event == "Inativa":
        c.execute('''UPDATE linen SET status = 0 WHERE (tag_id = ?)''', (tag_id,))
    elif event == "Danificada":
        c.execute('''UPDATE linen SET damage = 1 WHERE (tag_id = ?)''', (tag_id,))
    elif event == "Restaurada":
        c.execute('''UPDATE linen SET damage = 0 WHERE (tag_id = ?)''', (tag_id,))
    c.execute('''INSERT INTO log VALUES (:tag_id, :event_type, :date, :staff_name )''',{
        "tag_id": tag_id,
        "event_type": event,
        "date": data,
        "staff_name": staff_name
    })
    conn.commit()
    conn.close()
    return "OK"


if __name__ == '__main__':
    app.run('0.0.0.0',port=9000) # iniciando o flask, foi especificado porta 9000 pois por padrao o flask usa 5000 e como foi testado primariamente num MacOS, ele ja usa essa porta para o Airplay pelo visto.
