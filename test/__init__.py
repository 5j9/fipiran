from json import loads
from unittest.mock import patch


disable_get = patch(
    'fipiran._http_get',
    side_effect=ConnectionError('_get should not be called during tests'),
)


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def json(self):
        return loads(self.content)


def patch_get(filename):
    with open(f'{__file__}/../testdata/{filename}', 'rb') as f:
        content = f.read()

    def fake_get(*_, **__):
        return FakeResponse(content)

    return patch('fipiran._http_get', fake_get)
