import re

from voluptuous import Invalid, Schema

resize_validator = re.compile(r'^([1-9]\d*)x([1-9]\d*)$')


def is_resize(s):
    result = resize_validator.match(s)
    if result is None:
        raise Invalid('Invalid resize')
    return [int(size) for size in result.groups()]


schema = Schema(
    {
        'source': str,
        'resize': is_resize,
    },
    required=True
)
