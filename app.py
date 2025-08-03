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
    body { font-family: Arial, sans-serif; margin: 2rem; background: #f0f2f5; }
    h1 { color: #333; }
    form { margin-bottom: 1rem; }
    input[type=number], select { padding: 0.5rem; margin-right: 0.5rem; }
    button { padding: 0.5rem 1rem; }
    .user { background: white; border-radius: 8px; padding: 1rem; margin-bottom: 1rem; box-shadow: 0 2px 5px rgba(0,0,0,0.1); display: flex; align-items: center; }
    .user img { border-radius: 50%; margin-right: 1rem; width: 80px; height: 80px; object-fit: cover; }
    .user-info { line-height: 1.4; }
  </style>
</head>
<body>
  <h1>Gerador de Usuários Fake</h1>
  <form method="get">
    <label>Quantidade: <input type="number" name="count" min="1" max="50" value="{{count}}" /></label>
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
    <p>Nenhum usuário gerado ainda.</p>
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
                # A API fakerapi.it não oferece filtro de gênero nem nacionalidade, ignoramos esses filtros
                usuarios.append({
                    'name': f"{u['firstname']} {u['lastname']}",
                    'email': u['email'],
                    'phone': u['phone'],
                    'country': u.get('country', 'Brasil'),
                    'picture': 'https://via.placeholder.com/150',  # Sem foto real, usamos placeholder
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
