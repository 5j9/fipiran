from unittest.mock import patch

import fipiran


RECORD_MODE = False
OFFLINE_MODE = True and not RECORD_MODE


def patch_session(filename):

    async def _fake_session_get(url: str, **kwargs) -> str | bytes:
        file = f'{__file__}/../testdata/{filename}'

        if OFFLINE_MODE:
            with open(file, 'rb') as f:
                content = f.read()
        else:
            async with fipiran.Session() as s:
                content = await (await s.get(url, **kwargs)).read()
            if RECORD_MODE:
                with open(file, 'wb') as f:
                    f.write(content)

        return content

    return patch('fipiran._session_get', _fake_session_get)
