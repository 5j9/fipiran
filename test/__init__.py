from json import loads
from unittest.mock import patch

import fipiran


OFFLINE_MODE = True
RECORD_MODE = False


def identity_fn(f):
    return f


class NoOPPatch:

    def start(self):
        return

    def stop(self):
        return


no_op_patch = NoOPPatch()


if OFFLINE_MODE is True:
    disable_get = patch(
        'fipiran._http_get',
        side_effect=ConnectionError(
            '_get should not be called in OFFLINE_MODE'))
else:
    disable_get = no_op_patch


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def json(self):
        return loads(self.data)


# noinspection PyProtectedMember
_original_http_get = fipiran._http_get


def patch_get(filename):
    if OFFLINE_MODE is False:
        return identity_fn

    if RECORD_MODE is True:
        def _http_get_recorder(*args, **kwargs):
            resp = _original_http_get(*args, **kwargs)
            data = resp.data
            with open(f'{__file__}/../testdata/{filename}', 'wb') as f:
                f.write(data)
            return resp
        return patch('fipiran._http_get', _http_get_recorder)

    with open(f'{__file__}/../testdata/{filename}', 'rb') as f:
        content = f.read()

    def fake_get(*_, **__):
        return FakeResponse(content)

    return patch('fipiran._http_get', fake_get)
