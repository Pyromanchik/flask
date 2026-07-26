from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# Хранилище объявлений (в реальном приложении — БД)
adverts = {}


@app.route('/')
def hello_world():
    return 'Hello World! REST API for Ads'


@app.route('/adverts', methods=['POST'])
def create_advert():
    """Создание нового объявления"""
    data = request.get_json()

    if not data or 'title' not in data or 'description' not in data or 'owner' not in data:
        return jsonify({'error': 'Missing required fields: title, description, owner'}), 400

    ad_id = str(uuid.uuid4())

    advert = {
        'id': ad_id,
        'title': data['title'],
        'description': data['description'],
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'owner': data['owner']
    }

    adverts[ad_id] = advert

    return jsonify(advert), 201


@app.route('/adverts', methods=['GET'])
def get_all_adverts():
    """Получение всех объявлений"""
    return jsonify(list(adverts.values())), 200


@app.route('/adverts/<ad_id>', methods=['GET'])
def get_advert(ad_id):
    """Получение объявления по ID (UUID-строка)"""
    if ad_id not in adverts:
        return jsonify({'error': 'Advert not found'}), 404

    return jsonify(adverts[ad_id]), 200


@app.route('/adverts/<ad_id>', methods=['PUT'])
def update_advert(ad_id):
    """Обновление объявления по ID (UUID-строка)"""
    if ad_id not in adverts:
        return jsonify({'error': 'Advert not found'}), 404

    data = request.get_json()
    advert = adverts[ad_id]

    if 'title' in data:
        advert['title'] = data['title']
    if 'description' in data:
        advert['description'] = data['description']

    return jsonify(advert), 200


@app.route('/adverts/<ad_id>', methods=['DELETE'])
def delete_advert(ad_id):
    """Удаление объявления по ID (UUID-строка)"""
    if ad_id not in adverts:
        return jsonify({'error': 'Advert not found'}), 404

    del adverts[ad_id]
    return jsonify({'message': 'Advert deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)