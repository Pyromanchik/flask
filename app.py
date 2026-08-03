import asyncio
import uuid
from datetime import datetime
from aiohttp import web


class AsyncStore:
    """
    Асинхронное хранилище данных с блокировкой для безопасного доступа.
    """
    def __init__(self):
        self.data = {}
        self.lock = asyncio.Lock()

    async def get(self, key):
        async with self.lock:
            return self.data.get(key)

    async def set(self, key, value):
        async with self.lock:
            self.data[key] = value

    async def delete(self, key):
        async with self.lock:
            if key in self.data:
                del self.data[key]
                return True
            return False

    async def list_all(self):
        async with self.lock:
            return list(self.data.values())


# Создаем глобальный экземпляр хранилища
store = AsyncStore()


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

    # Асинхронное сохранение
    await store.set(ad_id, advert)

    # Возврат 201 Created
    return web.json_response(advert, status=201)


async def get_all_adverts(request: web.Request) -> web.Response:
    """
    GET /adverts
    Возвращает список всех объявлений.
    """
    # Асинхронное получение списка
    adverts = await store.list_all()
    return web.json_response(adverts)


async def get_advert(request: web.Request) -> web.Response:
    """
    GET /adverts/{id}
    Возвращает конкретное объявление по ID.
    """
    ad_id = request.match_info.get('id')

    # Асинхронное получение
    advert = await store.get(ad_id)

    if not advert:
        return web.json_response(
            {"error": "Advert not found"},
            status=404
        )

    return web.json_response(advert)


async def update_advert(request: web.Request) -> web.Response:
    """
    PUT /adverts/{id}
    Обновляет объявление.
    """
    ad_id = request.match_info.get('id')

    # Получаем текущее объявление
    advert = await store.get(ad_id)

    if not advert:
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

    # Обновляем только переданные поля
    if 'title' in data:
        advert['title'] = data['title']
    if 'description' in data:
        advert['description'] = data['description']
    if 'owner' in data:
        advert['owner'] = data['owner']

    # Асинхронно сохраняем обновленные данные
    await store.set(ad_id, advert)

    return web.json_response(advert)


async def delete_advert(request: web.Request) -> web.Response:
    """
    DELETE /adverts/{id}
    Удаляет объявление.
    """
    ad_id = request.match_info.get('id')

    # Проверяем существование и удаляем асинхронно
    deleted = await store.delete(ad_id)

    if not deleted:
        return web.json_response(
            {"error": "Advert not found"},
            status=404
        )

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