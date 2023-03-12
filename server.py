import logging
import os.path

import aiofiles
from aiohttp import web
import asyncio

from aiohttp.web_request import Request

ARCHIVE_URL = "/archive/"
PHOTOS_PATH = "test_photos/"
BATCH_SIZE = 512_000  # размер порции для отдачи файла в байтах
ARCHIVE_FILE_NAME = "archive.zip"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def archive(request: Request) -> web.StreamResponse:
    """Хендлер формирования архива и скачивания его в файл"""

    archive_hash = request.match_info['archive_hash']
    folder_path = os.path.join(os.getcwd(), PHOTOS_PATH, archive_hash)

    if not (os.path.exists(folder_path) and os.path.isdir(folder_path)):
        logger.warning(f'Запрошена несуществующая папка {archive_hash}')
        raise web.HTTPNotFound(text='Архив не существует или был удален')

    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'multipart/x-mixed-replace',
            'CONTENT-DISPOSITION': f'attachment;filename={ARCHIVE_FILE_NAME}'
        }
    )

    cmd = f"(cd {os.path.join(PHOTOS_PATH, archive_hash)} && zip -r - .)"
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Отправляет клиенту HTTP заголовки
    await response.prepare(request)

    while True:

        archive_data = await proc.stdout.read(BATCH_SIZE)

        await response.write(archive_data)

        if proc.stdout.at_eof():
            break

    return response


async def handle_index_page(request):
    """Главная страница проекта"""

    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', archive),
    ])
    web.run_app(app)
