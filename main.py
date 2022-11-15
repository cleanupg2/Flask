from functools import wraps
import os
import re
import time
from flask import Flask, abort, jsonify, request, session
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
import sqlite3
import bcrypt
from user import User, Users
import tags

app = Flask(__name__)
app.secret_key = 'luladraoconquistoumeucoracao'

login_manager = LoginManager()
login_manager.init_app(app)

linen_cat = {
    "Banho": ["Toalha de banho", "Toalha de rosto", "Tapete banheiro"],
    "Cama": ["Lençol", "Fronha", "Edredom"]
}

regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def create_login_return(error_message=None, user=None):
    resp = jsonify({"error_message": error_message, "user": user})
    resp.headers.add('Set-Cookie','cross-site-cookie=bar; SameSite=None;Secure')
    return resp

def timeit(func):
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


@app.route("/login", methods=["POST"])
@timeit
def login():
    print(request.json)
    x = request.json
    print(current_user)
    if current_user.is_authenticated:
        return create_login_return(error_message="Este usuário já está logado!")
    user, err = Users.get_user_for_login(x["user_id"], x["pwd"])
    if user is not None:
        login_user(user)
        return create_login_return(user=user.to_dict(), error_message=err)
    else:
        return create_login_return(err)


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    print(current_user)
    logout_user()
    err = "Deslogado"
    return create_login_return(err)


@app.route("/current_user", methods=["POST"])
@login_required
def current_user_req():
    return jsonify(current_user.to_dict())


@timeit
def create_signup_return(message, clear_all=False):
    return jsonify({"message": message, "clear_all": clear_all})


@app.route("/signup", methods=["POST"])
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
    if re.fullmatch(regex_email, email):
        return create_signup_return("O email não é válido.")
    if len(pwd) < 8:
        return create_signup_return("A senha precisa ter um mínimo de 8 carácteres.")
    bpassword = pwd.encode('utf-8')
    hashed = bcrypt.hashpw(bpassword, bcrypt.gensalt())
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''INSERT INTO user_data VALUES (:user_id, :pass_hash, :name,:email, :auth, :admin)''', {
        'user_id': user_id,
        'name': name,
        'email': email,
        'pass_hash': hashed,
        'auth': True,
        'admin': False
    })
    conn.commit()
    conn.close()
    return create_signup_return("Conta Criada!", True)

@app.route("/check_tags", methods=["POST"])
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

@app.route("/reg_tags", methods=["POST"])
@login_required
def reg_tags():
    x = request.json
    tag_id = x["tag_id"]
    print(tag_id)
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
    c = conn.cursor()
    c.execute('''INSERT INTO linen VALUES (:tag_id, :aquisition_date, :category, :sub_category, :supplier, :clean, :damage, :status, :staff_name)''',{
        'tag_id': tag_id,
        'aquisition_date': aquisition_date,
        'category': category,
        'sub_category': sub_category,
        'supplier': supplier,
        'clean': clean,
        'damage': damage,
        'status': status,
        'staff_name': staff_name
    })
    conn.commit()
    conn.close()
    return "Registrado"

@app.route("/total_tags", methods = ["GET"])
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

if __name__ == '__main__':
    app.run('0.0.0.0',port=9000)
