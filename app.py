from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os

app = Flask(__name__)
app.secret_key = 'chave_secreta'  # Importante para gerenciar sessões

# Função para carregar usuários do JSON
def load_users():
    with open('user.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return {user["user"]: user["password"] for user in data["data"]}

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
            return render_template('login.html', error="Usuário ou senha incorretos!")

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

if __name__ == '__main__':
    app.run(debug=True)
