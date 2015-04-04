import io
from urllib.parse import parse_qs, urlparse

import aiohttp
import asyncio
from aiohttp import web
from PIL import Image


@asyncio.coroutine
def init(loop, host, port):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', handle)

    srv = yield from loop.create_server(app.make_handler(), host, port)
    print('Server started at http://{}:{}'.format(host, port))
    return srv


@asyncio.coroutine
def handle(request):
    print(request.path_qs)
    query_components = parse_qs(urlparse(request.path_qs).query)
    url = query_components['source'][0]
    resize = list(map(int, query_components['resize'][0].split('x')))

    data = yield from download_file(url)
    img = Image.open(data)
    img.thumbnail(resize)

    stream = web.StreamResponse()
    stream.content_type = 'image/jpeg'
    stream.start(request)
    img.save(stream, format='JPEG')
    return stream


@asyncio.coroutine
def download_file(url):
    req = yield from aiohttp.request('GET', url)
    fd = io.BytesIO()
    while True:
        chunk = yield from req.content.read(1024)
        if not chunk:
            break
        fd.write(chunk)
    fd.seek(0)
    return fd

HOST = '0.0.0.0'
PORT = 8000

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop, HOST, PORT))
loop.run_forever()
