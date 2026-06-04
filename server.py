from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import re
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# 🔑 YANDEXGPT API
YANDEX_API_KEY = "AQVNyJjL-slW40rTCEGR8a_O0MfHjNnWEAd5kwmf"  # Ваш ключ
FOLDER_ID = "b1gpc79uc6813e585opd"
YANDEX_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/api/generate-game', methods=['POST'])
def generate_game():
    try:
        data = request.json
        user_prompt = data.get('prompt', '')
        
        print(f"\n{'='*70}")
        print(f"🎮 Генерация игры через ИИ")
        print(f"{'='*70}")
        print(f"📝 Промт: {user_prompt[:200]}...")
        
        # Запрос к YandexGPT
        payload = {
            "modelUri": f"gpt://{FOLDER_ID}/yandexgpt/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.8,
                "maxTokens": "8000"
            },
            "messages": [
                {
                    "role": "system",
                    "text": "Ты профессиональный разработчик игр. Создаёшь полноценные HTML5 игры на Canvas. Отвечаешь ТОЛЬКО кодом, без пояснений."
                },
                {
                    "role": "user",
                    "text": user_prompt
                }
            ]
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "x-folder-id": FOLDER_ID
        }
        
        print(f"📡 Отправка запроса к YandexGPT...")
        response = requests.post(YANDEX_API_URL, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            return jsonify({
                'success': False,
                'error': f'API error: {response.status_code}'
            }), 500
        
        result = response.json()
        game_code = result['result']['alternatives'][0]['message']['text']
        
        # Очистка кода от markdown
        game_code = clean_game_code(game_code)
        
        if not game_code.lower().strip().startswith('<!doctype'):
            return jsonify({
                'success': False,
                'error': 'Invalid response from AI'
            }), 500
        
        print(f"✅ Игра сгенерирована! Размер: {len(game_code)} символов")
        print(f"{'='*70}\n")
        
        return jsonify({
            'success': True,
            'game_code': game_code
        })
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def clean_game_code(code):
    """Очистка кода от markdown маркеров"""
    code = re.sub(r'^```\s*html?\s*\n?', '', code, flags=re.IGNORECASE)
    code = re.sub(r'^```\s*\n?', '', code)
    code = re.sub(r'\n?\s*```\s*$', '', code)
    
    doctype_match = re.search(r'<!DOCTYPE\s+html', code, re.IGNORECASE)
    if doctype_match:
        code = code[doctype_match.start():]
    
    html_end_match = re.search(r'</html>', code, re.IGNORECASE)
    if html_end_match:
        code = code[:html_end_match.end()]
    
    return code.strip()

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🎮 GameAI Generator Server с ИИ")
    print("="*70)
    print(f"📡 http://localhost:5000")
    print(f"🎨 Создать игру: http://localhost:5000/create-game.html")
    print(f"🎮 Мои игры: http://localhost:5000/my-games.html")
    print("="*70 + "\n")
    app.run(debug=True)