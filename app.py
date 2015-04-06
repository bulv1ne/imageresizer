import io
from urllib.parse import parse_qsl, urlparse

import aiohttp
import asyncio
from aiohttp import web
from PIL import Image
from validation import schema
from voluptuous import MultipleInvalid


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
    query_components = dict(parse_qsl(urlparse(request.path_qs).query))
    try:
        query_components = schema(query_components)
    except MultipleInvalid:
        raise web.HTTPBadRequest

    url = query_components['source']
    resize = query_components['resize']

    data = yield from download_file(url)
    try:
        img = Image.open(data)
    except OSError:
        raise web.HTTPBadRequest
    try:
        img.thumbnail(resize)
    except IndexError:
        raise web.HTTPBadRequest

    return stream_from_image(img, request=request)


@asyncio.coroutine
def download_file(url):
    req = yield from aiohttp.request('GET', url)
    if req.status == 404:
        raise web.HTTPNotFound
    fd = io.BytesIO()
    while True:
        chunk = yield from req.content.read(1024)
        if not chunk:
            break
        fd.write(chunk)
    fd.seek(0)
    return fd


def stream_from_image(img, request):
    stream = web.StreamResponse()
    stream.content_type = 'image/' + img.format.lower()
    stream.start(request)
    img.save(stream, format=img.format)
    return stream

HOST = '0.0.0.0'
PORT = 8000

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop, HOST, PORT))
loop.run_forever()
