from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import pyotp
import qrcode

app = Flask(__name__)
app.secret_key = 'chave_secreta'  # Importante para gerenciar sessões

# Caminho do arquivo JSON
JSON_FILE = 'user.json'

# Função para carregar usuários do JSON
def load_users():
    if not os.path.exists(JSON_FILE):
        return {}  # Retorna um dicionário vazio se o arquivo não existir

    with open(JSON_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
        #return {user["user"]: user["password"] for user in data["data"]}
        # Retorna um dicionário com todos os dados de cada usuário
        return {user["user"]: user for user in data["data"]}

# Função para salvar novo usuário no JSON
def save_user(username, password):
    users = load_users()

    # Verifica se o usuário já existe
    if username in users:
        return False  # Retorna falso se o usuário já existir

    # Gera a key com pyotp
    key = pyotp.random_base32()

    link = pyotp.TOTP(key).provisioning_uri(name=f"Teste de OTP do {username}", issuer_name="Autenticador")
    img_qrcode = qrcode.make(link)
    img_qrcode.save('static/qrcode.png')

    # Lê o JSON completo para adicionar o novo usuário
    with open(JSON_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Adiciona o novo usuário com a key
    data["data"].append({
        "user": username,
        "password": password,
        "key": key
    })

    # Salva de volta no arquivo
    with open(JSON_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return True  # Retorna verdadeiro se o cadastro for bem-sucedido

# Rota da tela de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Se for o segundo POST (com OTP)
        if 'otp_code' in request.form:
            username = session.get('temp_user')
            password = session.get('temp_pass')
            otp_code = request.form['otp_code']
            users = load_users()

            if username in users and users[username]['password'] == password:
                if pyotp.TOTP(users[username]['key']).verify(otp_code):
                    session.pop('temp_user')
                    session.pop('temp_pass')
                    session['user'] = username
                    return redirect(url_for('home'))
                else:
                    flash("Código de autenticação incorreto!", "error")
            else:
                flash("Usuário ou senha inválidos", "error")

        else:
            # Primeiro POST com username e password
            username = request.form['username']
            password = request.form['password']
            users = load_users()

            if username in users and users[username]['password'] == password:
                session['temp_user'] = username
                session['temp_pass'] = password
                return render_template('login.html', show_otp_modal=True, username=username)
            else:
                flash("Usuário ou senha incorretos!", "error")

    return render_template('login.html')

# Rota da página protegida
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('home.html', username=session['user'])

# Rota para logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Rota para criar um novo usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    show_qrcode = False

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if save_user(username, password):
            flash("Usuário cadastrado com sucesso! Faça login.", "success")
            show_qrcode = True
        else:
            flash("Usuário já existe! Escolha outro nome.", "error")

    return render_template('register.html', show_qrcode=show_qrcode)

@app.route('/finalizar')
def finalizar():
    qrcode_path = os.path.join(app.static_folder, 'qrcode.png')
    if os.path.exists(qrcode_path):
        os.remove(qrcode_path)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
