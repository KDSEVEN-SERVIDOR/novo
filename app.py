from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta
import secrets
import pytz  # Para trabalhar com timezones

app = Flask(__name__)

# Dicionário para armazenar as chaves (em produção, use um banco de dados)
keys_db = {}

def get_current_time():
    """Obtém a data/hora atual com timezone (usando internet indiretamente via servidor)"""
    return datetime.now(pytz.timezone('America/Sao_Paulo'))  # Altere para seu timezone

def generate_temp_key(valid_minutes=60):
    """Gera uma chave temporária válida por X minutos"""
    current_time = get_current_time()
    expiry_time = current_time + timedelta(minutes=valid_minutes)
    
    # Gera uma chave aleatória segura
    key = secrets.token_urlsafe(32)
    
    # Armazena a chave com seu tempo de expiração
    keys_db[key] = {
        'created_at': current_time.isoformat(),
        'expires_at': expiry_time.isoformat(),
        'is_valid': True
    }
    
    return key

def validate_key(key):
    """Verifica se uma chave é válida e não expirou"""
    if key not in keys_db:
        return False
    
    key_data = keys_db[key]
    if not key_data['is_valid']:
        return False
    
    expiry_time = datetime.fromisoformat(key_data['expires_at'])
    return get_current_time() < expiry_time

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-key', methods=['POST'])
def generate_key():
    valid_minutes = int(request.form.get('valid_minutes', 60))
    key = generate_temp_key(valid_minutes)
    return jsonify({
        'key': key,
        'expires_at': keys_db[key]['expires_at'],
        'valid_minutes': valid_minutes
    })

@app.route('/validate-key/<key>')
def validate_key_route(key):
    is_valid = validate_key(key)
    return jsonify({'valid': is_valid})

if __name__ == '__main__':
    app.run(debug=True)