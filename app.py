from flask import Flask, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

# Хранилище объявлений (в реальном приложении это была бы база данных)
adverts = {}


@app.route('/')
def hello_world():
    return 'Hello World! REST API for Ads'


@app.route('/adverts', methods=['POST'])
def create_advert():
    """Создание нового объявления"""
    data = request.get_json()

    # Проверка обязательных полей
    if not data or 'title' not in data or 'description' not in data or 'owner' not in data:
        return jsonify({'error': 'Missing required fields: title, description, owner'}), 400

    # Генерация уникального ID
    ad_id = str(uuid.uuid4())

    # Создание объявления
    advert = {
        'id': ad_id,
        'title': data['title'],
        'description': data['description'],
        'created_at': datetime.utcnow().isoformat() + 'Z',  # UTC время в ISO формате
        'owner': data['owner']
    }

    # Сохранение объявления
    adverts[ad_id] = advert

    return jsonify(advert), 201


@app.route('/adverts', methods=['GET'])
def get_all_adverts():
    """Получение всех объявлений"""
    return jsonify(list(adverts.values())), 200


@app.route('/adverts/<int:ad_id>', methods=['GET'])
def get_advert(ad_id):
    """Получение объявления по ID"""
    # Примечание: в данном примере ad_id - строка (UUID), но для совместимости с запросом
    # можно использовать int, если хотите использовать числовые ID.
    # Здесь я использую str(ad_id) для совместимости с uuid, который создается в create_advert
    # Если вы хотите использовать числовые ID, замените uuid на int и убедитесь в уникальности

    # Для UUID:
    ad_id_str = str(ad_id)
    if ad_id_str not in adverts:
        # Попытка найти как int, если был передан int вместо UUID
        if str(ad_id) in adverts:
            return jsonify(adverts[str(ad_id)]), 200
        else:
            return jsonify({'error': 'Advert not found'}), 404

    return jsonify(adverts[ad_id_str]), 200


@app.route('/adverts/<int:ad_id>', methods=['PUT'])
def update_advert(ad_id):
    """Обновление объявления"""
    data = request.get_json()

    # Проверка наличия объявления
    ad_id_str = str(ad_id)
    if ad_id_str not in adverts:
        return jsonify({'error': 'Advert not found'}), 404

    advert = adverts[ad_id_str]

    # Обновление полей, если они переданы
    if 'title' in data:
        advert['title'] = data['title']
    if 'description' in data:
        advert['description'] = data['description']
    # created_at и owner обычно не меняются при обновлении, но можно добавить логику

    return jsonify(advert), 200


@app.route('/adverts/<int:ad_id>', methods=['DELETE'])
def delete_advert(ad_id):
    """Удаление объявления"""
    ad_id_str = str(ad_id)
    if ad_id_str not in adverts:
        return jsonify({'error': 'Advert not found'}), 404

    del adverts[ad_id_str]
    return jsonify({'message': 'Advert deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)