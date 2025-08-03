from flask import Flask, request, render_template_string
import requests
import logging
from faker import Faker

app = Flask(__name__)
fake = Faker('pt_BR')

TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <title>Gerador de Usuários Fake</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      margin: 2rem;
      background: linear-gradient(135deg, #a8edea, #fed6e3);
      color: #333;
    }
    h1 {
      color: #4a4a4a;
      text-align: center;
      margin-bottom: 2rem;
      text-shadow: 1px 1px 2px #fff;
    }
    form {
      background: #fff;
      padding: 1rem 1.5rem;
      border-radius: 10px;
      max-width: 400px;
      margin: 0 auto 2rem auto;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
      display: flex;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
      align-items: center;
    }
    input[type=number], select {
      padding: 0.5rem;
      border-radius: 6px;
      border: 1px solid #ccc;
      font-size: 1rem;
      min-width: 90px;
      box-sizing: border-box;
      transition: border-color 0.3s;
    }
    input[type=number]:focus, select:focus {
      border-color: #f48fb1;
      outline: none;
    }
    button {
      background-color: #f48fb1;
      border: none;
      color: white;
      font-weight: bold;
      padding: 0.6rem 1.2rem;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.3s;
      min-width: 90px;
    }
    button:hover {
      background-color: #d81b60;
    }
    .user {
      background: white;
      border-radius: 10px;
      padding: 1rem 1.5rem;
      margin-bottom: 1rem;
      box-shadow: 0 4px 12px rgba(244, 143, 177, 0.3);
      max-width: 500px;
      margin-left: auto;
      margin-right: auto;
      color: #444;
      font-weight: 500;
      line-height: 1.5;
      transition: transform 0.2s ease;
    }
    .user:hover {
      transform: scale(1.02);
      box-shadow: 0 6px 15px rgba(244, 143, 177, 0.6);
    }
  </style>
</head>
<body>
  <h1>Gerador de Usuários Fake</h1>
  <form method="get">
    <label>Quantidade:
      <input type="number" name="count" min="1" max="50" value="{{count}}" />
    </label>
    <label>Gênero:
      <select name="gender">
        <option value="" {% if gender == '' %}selected{% endif %}>Todos</option>
        <option value="male" {% if gender == 'male' %}selected{% endif %}>Masculino</option>
        <option value="female" {% if gender == 'female' %}selected{% endif %}>Feminino</option>
      </select>
    </label>
    <button type="submit">Gerar</button>
  </form>
  
  {% if usuarios %}
    {% for user in usuarios %}
      <div class="user">
        <strong>{{ user.name }}</strong><br/>
        Email: {{ user.email }}<br/>
        Telefone: {{ user.phone }}<br/>
        País: {{ user.country }}<br/>
        CPF: {{ user.cpf }}
      </div>
    {% endfor %}
  {% else %}
    <p style="text-align: center; color: #666;">Nenhum usuário gerado ainda.</p>
  {% endif %}
</body>
</html>
"""

def gerar_usuarios(count=5, gender=None, nat=None):
    url = f'https://fakerapi.it/api/v1/persons?_quantity={count}'
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            dados = resp.json().get('data', [])
            usuarios = []
            for u in dados:
                usuarios.append({
                    'name': f"{u['firstname']} {u['lastname']}",
                    'email': u['email'],
                    'phone': u['phone'],
                    'country': u.get('country', 'Brasil'),
                    'cpf': fake.cpf()
                })
            return usuarios
        else:
            logging.warning(f"Erro na API fakerapi: status {resp.status_code}")
    except Exception as e:
        logging.warning(f"Exceção ao buscar usuários: {e}")
    return []

@app.route('/', methods=['GET'])
def index():
    count = request.args.get('count', default=5, type=int)
    gender = request.args.get('gender', default='', type=str)
    nat = request.args.get('nat', default='', type=str)
    
    usuarios = gerar_usuarios(count, gender, nat)
    logging.warning(f"Gerados {len(usuarios)} usuários | gender={gender} | nat={nat}")
    
    return render_template_string(TEMPLATE, usuarios=usuarios, count=count, gender=gender, nat=nat)

if __name__ == '__main__':
    app.run(debug=True)
