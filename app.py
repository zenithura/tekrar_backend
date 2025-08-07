
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
# CORS ayarları - Tüm origin'lere izin ver ve preflight isteklerini destekle
CORS(app, 
     origins=['*'], 
     methods=['GET', 'POST', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=False)

CODE_FILE = 'code.txt'

def read_codes():
    codes = {}
    try:
        with open(CODE_FILE, 'r') as f:
            for line in f:
                parts = line.strip().split(',')
                if len(parts) == 2:
                    codes[parts[0]] = int(parts[1])
    except FileNotFoundError:
        pass
    return codes

def write_codes(codes):
    with open(CODE_FILE, 'w') as f:
        for code, value in codes.items():
            f.write(f"{code},{value}\n")

@app.route('/api/check_code', methods=['POST', 'OPTIONS'])
def check_code():
    # OPTIONS isteği için CORS preflight
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.get_json()
    code_to_check = data.get('code')

    if not code_to_check:
        return jsonify({'status': 'error', 'message': 'Code not provided'}), 400

    codes = read_codes()

    if code_to_check in codes:
        if codes[code_to_check] == 0:
            codes[code_to_check] = 1
            write_codes(codes)
            return jsonify({
                'status': 'success', 
                'allowed': True, 
                'message': 'Girişe izin verildi.',
                'token': f'license_{code_to_check}'
            })
        else:
            return jsonify({
                'status': 'error', 
                'allowed': False, 
                'message': 'Kod daha önce kullanılmış veya geçersiz.'
            }), 403
    else:
        return jsonify({
            'status': 'error', 
            'allowed': False, 
            'message': 'Kod bulunamadı.'
        }), 404

@app.route('/api/verify_token', methods=['POST', 'OPTIONS'])
def verify_token():
    # Token doğrulama endpoint'i
    if request.method == 'OPTIONS':
        return jsonify({'status': 'ok'}), 200
    
    data = request.get_json()
    token = data.get('token')
    
    if not token or not token.startswith('license_'):
        return jsonify({'status': 'error', 'valid': False}), 400
    
    # Token'dan kod çıkar
    code = token.replace('license_', '')
    codes = read_codes()
    
    # Kod kullanılmış mı kontrol et
    if code in codes and codes[code] == 1:
        return jsonify({'status': 'success', 'valid': True})
    else:
        return jsonify({'status': 'error', 'valid': False}), 403

if __name__ == '__main__':
    app.run(debug=True)