# imageresizer

## Start

```sh
docker run -ti --rm -p 8000:8000 bulv1ne/imageresizer
# OR as a daemon
docker run -d -p 8000:8000 bulv1ne/imageresizer
```

Then visit the url:
http://127.0.0.1:8000/?resize=100x100&source=https://placekitten.com/g/200/300


## Nginx proxy cache

```
proxy_cache_path /data/nginx/cache keys_zone=img_resize:100m max_size=1g inactive=30d;

server {
    listen 80;
    server_name example.com

    location /resize {
        proxy_pass http://127.0.0.1:8000/; # The running docker container
        proxy_cache img_resize;
        proxy_cache_key $request_uri;
        proxy_cache_valid 30d;
        proxy_hide_header Set-Cookie;
        proxy_ignore_headers "Set-Cookie";
        expires max;
        add_header Pragma public;
        add_header Cache-Control "public";
        add_header X-Proxy-Cache $upstream_cache_status;
    }

    # ... more location configuration
}
```

Then the new url will be:

http://example.com/resize?resize=100x100&source=https://placekitten.com/g/200/300

First time it will load as slow as usual, second time it will return the cached response.

More info:
- [Caching guide](http://nginx.com/resources/admin-guide/caching/)
- [Http proxy module](http://nginx.org/en/docs/http/ngx_http_proxy_module.html)
