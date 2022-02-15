from json import loads
from unittest.mock import patch

import fipiran


RECORD_MODE = False
OFFLINE_MODE = True and not RECORD_MODE


def identity_fn(f):
    return f


class NoOPPatch:

    def start(self):
        return

    def stop(self):
        return


if OFFLINE_MODE is True:
    disable_get = patch(
        'fipiran._http_get',
        side_effect=NotImplementedError(
            '_http_get should not be called in OFFLINE_MODE'))
else:
    disable_get = NoOPPatch()


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return loads(self.data)


# noinspection PyProtectedMember
_original_http_get = fipiran._http_get


def patch_get(filename):
    if RECORD_MODE is True:
        def _http_get_recorder(*args, **kwargs):
            resp = _original_http_get(*args, **kwargs)
            data = resp.data
            with open(f'{__file__}/../testdata/{filename}', 'wb') as f:
                f.write(data)
            return resp
        return patch('fipiran._http_get', _http_get_recorder)

    if OFFLINE_MODE is False:
        return identity_fn

    with open(f'{__file__}/../testdata/{filename}', 'rb') as f:
        content = f.read()

    def fake_get(*_, **__):
        return FakeResponse(content)

    return patch('fipiran._http_get', fake_get)
