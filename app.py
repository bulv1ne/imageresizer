import io
from urllib.parse import parse_qsl, urlparse

import aiohttp
from aiohttp import web
from PIL import Image
from voluptuous import MultipleInvalid

from validation import schema


def main(host, port):
    app = web.Application()
    app.add_routes([web.get("/", handle)])

    print("Server started at http://{}:{}".format(host, port))
    web.run_app(app, host=host, port=port)


async def handle(request):
    print(request.path_qs)
    query_components = dict(parse_qsl(urlparse(request.path_qs).query))
    try:
        query_components = schema(query_components)
    except MultipleInvalid:
        raise web.HTTPBadRequest

    url = query_components["source"]
    resize = query_components["resize"]

    data = await download_file(url)
    try:
        img = Image.open(data)
    except OSError:
        raise web.HTTPBadRequest
    try:
        img.thumbnail(resize)
    except IndexError:
        raise web.HTTPBadRequest

    return await stream_from_image(img, request=request)


async def download_file(url):
    async with aiohttp.ClientSession() as session:
        req = await session.get(url)
        if req.status == 404:
            raise web.HTTPNotFound
        fd = io.BytesIO()
        while True:
            chunk = await req.content.read(1024)
            if not chunk:
                break
            fd.write(chunk)
        fd.seek(0)
        return fd


async def stream_from_image(img, request):
    stream = web.StreamResponse()
    stream.content_type = "image/" + img.format.lower()
    await stream.prepare(request)
    data = io.BytesIO()
    img.save(data, format=img.format)
    await stream.write(data.getvalue())
    return stream


HOST = "0.0.0.0"
PORT = 8000

if __name__ == "__main__":
    main(HOST, PORT)
