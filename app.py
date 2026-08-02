import asyncio
import uuid
from datetime import datetime
from aiohttp import web

# Глобальное хранилище (в памяти).
# В реальном проекте здесь была бы асинхронная база данных (например, AsyncPG для PostgreSQL)
adverts_db = {}


async def create_advert(request: web.Request) -> web.Response:
    """
    POST /adverts
    Создает новое объявление.
    """
    try:
        data = await request.json()
    except Exception:
        return web.json_response(
            {"error": "Invalid JSON body"},
            status=400
        )

    # Валидация обязательных полей
    required_fields = ['title', 'description', 'owner']
    if not all(field in data for field in required_fields):
        missing = [f for f in required_fields if f not in data]
        return web.json_response(
            {"error": f"Missing required fields: {', '.join(missing)}"},
            status=400
        )

    # Генерация UUID
    ad_id = str(uuid.uuid4())

    # Формирование объекта объявления
    advert = {
        "id": ad_id,
        "title": data["title"],
        "description": data["description"],
        "owner": data["owner"],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    # Сохранение в "БД"
    adverts_db[ad_id] = advert

    # Возврат 201 Created
    return web.json_response(advert, status=201)


async def get_all_adverts(request: web.Request) -> web.Response:
    """
    GET /adverts
    Возвращает список всех объявлений.
    """
    return web.json_response(list(adverts_db.values()))


async def get_advert(request: web.Request) -> web.Response:
    """
    GET /adverts/{id}
    Возвращает конкретное объявление по ID.
    """
    ad_id = request.match_info.get('id')

    if ad_id not in adverts_db:
        return web.json_response(
            {"error": "Advert not found"},
            status=404
        )

    return web.json_response(adverts_db[ad_id])


async def update_advert(request: web.Request) -> web.Response:
    """
    PUT /adverts/{id}
    Обновляет объявление.
    """
    ad_id = request.match_info.get('id')

    if ad_id not in adverts_db:
        return web.json_response(
            {"error": "Advert not found"},
            status=404
        )

    try:
        data = await request.json()
    except Exception:
        return web.json_response(
            {"error": "Invalid JSON body"},
            status=400
        )

    advert = adverts_db[ad_id]

    # Обновляем только переданные поля
    if 'title' in data:
        advert['title'] = data['title']
    if 'description' in data:
        advert['description'] = data['description']
    if 'owner' in data:
        advert['owner'] = data['owner']

    # Можно обновить время последнего изменения, если нужно:
    # advert['updated_at'] = datetime.utcnow().isoformat() + "Z"

    return web.json_response(advert)


async def delete_advert(request: web.Request) -> web.Response:
    """
    DELETE /adverts/{id}
    Удаляет объявление.
    """
    ad_id = request.match_info.get('id')

    if ad_id not in adverts_db:
        return web.json_response(
            {"error": "Advert not found"},
            status=404
        )

    del adverts_db[ad_id]

    return web.json_response(
        {"message": "Advert deleted successfully"},
        status=200
    )


async def init_app() -> web.Application:
    """
    Конфигурация приложения и регистрация роутов.
    """
    app = web.Application()

    # Регистрация обработчиков с указанием HTTP-методов
    app.router.add_post('/adverts', create_advert)
    app.router.add_get('/adverts', get_all_adverts)
    app.router.add_get('/adverts/{id}', get_advert)
    app.router.add_put('/adverts/{id}', update_advert)
    app.router.add_delete('/adverts/{id}', delete_advert)

    return app


if __name__ == '__main__':
    # Запуск сервера в async режиме
    web.run_app(init_app(), host='127.0.0.1', port=5000)