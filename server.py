import aiofiles
from aiohttp import web, MultipartWriter
import asyncio

from aiohttp.web_request import Request

ARCHIVE_URL = "/archive/"
PHOTOS_PATH = "test_photos/"
BATCH_SIZE = 512_000  # размер порции для отдачи файла в байтах
ARCHIVE_FILE_NAME = "archive.zip"


async def handle_index_page(request):
    async with aiofiles.open('index.html', mode='r') as index_file:
        index_contents = await index_file.read()
    return web.Response(text=index_contents, content_type='text/html')


async def download_handler(request: Request) -> web.StreamResponse:
    """Хендлер формирования архива и скачивания его в файл"""

    response = web.StreamResponse(
        status=200,
        reason='OK',
        headers={
            'Content-Type': 'multipart/x-mixed-replace',
            'CONTENT-DISPOSITION': f'attachment;filename={ARCHIVE_FILE_NAME}'
        }
    )

    archive_hash = request.match_info.get('archive_hash')

    cmd = " ".join(["zip", "-rj", "-", PHOTOS_PATH + archive_hash])
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Отправляет клиенту HTTP заголовки
    await response.prepare(request)

    while True:

        archive_data = await proc.stdout.read(BATCH_SIZE)

        # Отправляет клиенту очередную порцию файла
        with MultipartWriter('text/plain') as mpwriter:
            mpwriter.append(archive_data)
            await mpwriter.write(response)

        if proc.stdout.at_eof():
            break

    return response


if __name__ == '__main__':
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index_page),
        web.get('/archive/{archive_hash}/', download_handler),
    ])
    web.run_app(app)
