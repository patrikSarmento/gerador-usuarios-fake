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
      margin: 2rem auto;
      max-width: 800px;
      background: #f9fafb;
      color: #222;
      padding: 1rem;
    }
    h1 {
      text-align: center;
      color: #444;
      margin-bottom: 2rem;
    }
    form {
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-bottom: 2rem;
      flex-wrap: wrap;
    }
    input[type=number], select {
      padding: 0.5rem;
      font-size: 1rem;
      border: 1px solid #ccc;
      border-radius: 4px;
      min-width: 120px;
    }
    button {
      padding: 0.5rem 1.2rem;
      background-color: #4a90e2;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: bold;
      transition: background-color 0.3s ease;
    }
    button:hover {
      background-color: #357ABD;
    }
    .user {
      background: white;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
      box-shadow: 0 3px 8px rgba(0,0,0,0.1);
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .user img {
      border-radius: 50%;
      width: 80px;
      height: 80px;
      object-fit: cover;
      border: 2px solid #4a90e2;
    }
    .user-info {
      line-height: 1.5;
      font-size: 1rem;
    }
    .user-info strong {
      font-size: 1.1rem;
      color: #222;
    }
    p.no-users {
      text-align: center;
      color: #888;
      font-style: italic;
      margin-top: 2rem;
    }
    @media (max-width: 600px) {
      form {
        flex-direction: column;
        align-items: center;
      }
      input[type=number], select, button {
        min-width: 100%;
        max-width: 300px;
      }
      .user {
        flex-direction: column;
        align-items: center;
        text-align: center;
      }
      .user img {
        margin-bottom: 0.5rem;
      }
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
        <img src="{{ user.picture }}" alt="Foto de {{ user.name }}" />
        <div class="user-info">
          <strong>{{ user.name }}</strong><br/>
          Email: {{ user.email }}<br/>
          Telefone: {{ user.phone }}<br/>
          País: {{ user.country }}<br/>
          CPF: {{ user.cpf }}
        </div>
      </div>
    {% endfor %}
  {% else %}
    <p class="no-users">Nenhum usuário gerado ainda.</p>
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
                    'picture': 'https://via.placeholder.com/150',
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
