from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

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
        return {user["user"]: user["password"] for user in data["data"]}

# Função para salvar novo usuário no JSON
def save_user(username, password):
    users = load_users()

    # Verifica se o usuário já existe
    if username in users:
        return False  # Retorna falso se o usuário já existir

    # Lê o JSON completo para adicionar o novo usuário
    with open(JSON_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    data["data"].append({"user": username, "password": password})  # Adiciona o novo usuário

    # Salva de volta no arquivo
    with open(JSON_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

    return True  # Retorna verdadeiro se o cadastro for bem-sucedido

# Rota da tela de login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()

        if username in users and users[username] == password:
            session['user'] = username
            return redirect(url_for('home'))
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
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if save_user(username, password):
            flash("Usuário cadastrado com sucesso! Faça login.", "success")
            return redirect(url_for('login'))
        else:
            flash("Usuário já existe! Escolha outro nome.", "error")

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
