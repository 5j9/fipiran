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
        'fipiran._get',
        side_effect=NotImplementedError('_get should not be called in OFFLINE_MODE'),
    )
else:
    disable_get = NoOPPatch()


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def json(self):
        return loads(self.content)


# noinspection PyProtectedMember
_original_get = fipiran._get


def patch_get(filename):
    if RECORD_MODE is True:

        def _get_recorder(*args, **kwargs):
            resp = _original_get(*args, **kwargs)
            content = resp.content
            with open(f'{__file__}/../testdata/{filename}', 'wb') as f:
                f.write(content)
            return resp

        return patch('fipiran._get', _get_recorder)

    if OFFLINE_MODE is False:
        return identity_fn

    with open(f'{__file__}/../testdata/{filename}', 'rb') as f:
        content = f.read()

    def fake_get(*_, **__):
        return FakeResponse(content)

    return patch('fipiran._get', fake_get)
