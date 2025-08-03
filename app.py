from flask import Flask, render_template_string, request, send_file
import requests
import csv
import json
import io
from faker import Faker
import os
import logging

app = Flask(__name__)
fake = Faker('pt_BR')

logging.basicConfig(level=logging.WARNING)

PAISES_PT = {
    "Brazil": "Brasil",
    "United States": "Estados Unidos",
    "France": "França",
    "Germany": "Alemanha",
    "Spain": "Espanha",
    "United Kingdom": "Reino Unido",
    "Australia": "Austrália",
    "Canada": "Canadá",
    "Mexico": "México",
    "Norway": "Noruega",
    "Netherlands": "Holanda",
    "Switzerland": "Suíça",
    "Denmark": "Dinamarca",
    "Finland": "Finlândia",
    "Turkey": "Turquia",
    "Ireland": "Irlanda",
    "New Zealand": "Nova Zelândia",
    "Japan": "Japão",
    "South Korea": "Coreia do Sul"
}

TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Gerador de Usuários Fake</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(to right, #141e30, #243b55);
      color: #f8f9fa;
      font-family: 'Segoe UI', sans-serif;
      padding: 2rem;
    }
    .title {
      text-align: center;
      margin-bottom: 2rem;
      color: #ffc107;
      font-weight: 700;
      font-size: 2.5rem;
      text-shadow: 0 0 10px #ffc10799;
    }
    .form-control, .btn {
      border-radius: 10px;
    }
    .btn-warning {
      font-weight: 600;
      padding: 0.5rem 1.5rem;
    }
    .user-card {
      background: #2a2f40;
      border-radius: 15px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .avatar {
      border-radius: 50%;
      border: 4px solid #ffc107;
      box-shadow: 0 0 10px #ffc10780;
    }
    .user-info h5 {
      color: #ffc107;
      font-weight: 600;
    }
    .user-info p {
      margin: 0.3rem 0;
    }
    .icon {
      color: #ffc107;
      margin-right: 0.5rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1 class="title">👥 Gerador de Usuários Fakes</h1>
    <form method="get" class="row g-3 justify-content-center mb-4">
      <div class="col-md-2">
        <input type="number" name="count" min="1" max="20" class="form-control" placeholder="Qtd" value="{{ count or 5 }}">
      </div>
      <div class="col-md-2">
        <select name="gender" class="form-control">
          <option value="">Gênero</option>
          <option value="male" {% if gender == 'male' %}selected{% endif %}>Masculino</option>
          <option value="female" {% if gender == 'female' %}selected{% endif %}>Feminino</option>
        </select>
      </div>
      <div class="col-md-2">
        <select name="nat" class="form-control">
          <option value="">País</option>
          <option value="BR" {% if nat == 'BR' %}selected{% endif %}>Brasil</option>
          <option value="US" {% if nat == 'US' %}selected{% endif %}>EUA</option>
          <option value="FR" {% if nat == 'FR' %}selected{% endif %}>França</option>
        </select>
      </div>
      <div class="col-auto">
        <button class="btn btn-warning">Gerar</button>
      </div>
      {% if users %}
      <div class="col-auto">
        <a href="/export?format=json&count={{ count }}&gender={{ gender }}&nat={{ nat }}" class="btn btn-success">Exportar JSON</a>
        <a href="/export?format=csv&count={{ count }}&gender={{ gender }}&nat={{ nat }}" class="btn btn-primary">Exportar CSV</a>
      </div>
      {% endif %}
    </form>

    {% if users %}
      <div class="row">
        {% for user in users %}
          <div class="col-md-6">
            <div class="user-card d-flex align-items-center gap-4 flex-wrap">
              <img src="{{ user['picture'] }}" width="100" height="100" class="avatar" alt="Avatar do usuário">
              <div class="user-info">
                <h5>{{ user['name'] }}</h5>
                <p><i class="fa-solid fa-envelope icon"></i>{{ user['email'] }}</p>
                <p><i class="fa-solid fa-phone icon"></i>{{ user['phone'] }}</p>
                <p><i class="fa-solid fa-earth-americas icon"></i>{{ user['country'] }}</p>
                <p><i class="fa-solid fa-id-card icon"></i>CPF: {{ user['cpf'] }}</p>
              </div>
            </div>
          </div>
        {% endfor %}
      </div>
    {% endif %}
  </div>
</body>
</html>
"""

def traduzir_pais(pais_en):
    return PAISES_PT.get(pais_en, pais_en)

def gerar_usuarios(count=5, gender=None, nat=None):
    url = f'https://randomuser.me/api/?results={count}'

    if gender in ('male', 'female'):
        url += f'&gender={gender}'
    if nat and nat.strip():
        url += f'&nat={nat.upper()}'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            dados = resp.json().get('results', [])
            usuarios = []
            for u in dados:
                pais_traduzido = traduzir_pais(u['location']['country'])
                usuarios.append({
                    'name': f"{u['name']['first']} {u['name']['last']}",
                    'email': u['email'],
                    'phone': u['phone'],
                    'country': pais_traduzido,
                    'picture': u['picture']['large'],
                    'cpf': fake.cpf()
                })
            logging.warning(f"Gerados {len(usuarios)} usuários | gender={gender} | nat={nat}")
            return usuarios
        else:
            logging.warning(f"Erro na API randomuser: status {resp.status_code}")
    except Exception as e:
        logging.warning(f"Exceção ao buscar usuários: {e}")
    return []

@app.route('/')
def index():
    count = request.args.get('count', 5)
    gender = request.args.get('gender')
    nat = request.args.get('nat')
    try:
        count = int(count)
        count = max(1, min(count, 20))
    except ValueError:
        count = 5

    users = gerar_usuarios(count, gender, nat)
    return render_template_string(TEMPLATE, users=users, count=count, gender=gender, nat=nat)

@app.route('/export')
def export():
    format_type = request.args.get('format', 'json')
    count = int(request.args.get('count', 5))
    gender = request.args.get('gender')
    nat = request.args.get('nat')
    users = gerar_usuarios(count, gender, nat)

    if format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Nome', 'Email', 'Telefone', 'País', 'CPF'])
        for u in users:
            writer.writerow([u['name'], u['email'], u['phone'], u['country'], u['cpf']])
        output.seek(0)
        return send_file(io.BytesIO(output.read().encode()), mimetype='text/csv', as_attachment=True, download_name='usuarios.csv')

    else:
        json_data = json.dumps(users, indent=2, ensure_ascii=False)
        return send_file(io.BytesIO(json_data.encode()), mimetype='application/json', as_attachment=True, download_name='usuarios.json')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
