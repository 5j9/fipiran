__version__ = '0.9.1.dev0'
from json import loads

from aiohttp import ClientSession as _ClientSession, \
    ClientTimeout as _ClientTimeout, ClientResponse as _ClientResponse

# noinspection PyUnresolvedReferences
from pandas import (
    DataFrame as _DataFrame,
    read_html as _read_html,
    to_datetime as _to_datetime,
)

# noinspection PyUnresolvedReferences
from jdatetime import datetime as _jdatetime


_FIPIRAN = 'https://www.fipiran.ir/'
_YK = ''.maketrans('يك', 'یک')
_API = 'https://fund.fipiran.ir/api/v1/'
SESSION : _ClientSession | None = None


class Session(_ClientSession):

    def __init__(self, **kwargs):
        if 'timeout' not in kwargs:
            kwargs['timeout'] = _ClientTimeout(
                total=60, sock_connect=10, sock_read=10)
        super().__init__(**kwargs)

    async def __aenter__(self) -> _ClientSession:
        global SESSION
        SESSION = await super().__aenter__()
        return SESSION


# this function should only be called from _get below
async def _session_get(url, **kwargs) -> bytes:
    return await (await SESSION.get(url, **kwargs)).read()


async def _api(path) -> dict | list:
    return loads(await _session_get(_API + path))


async def _fipiran(path: str, params=None, json_resp=False) -> str | dict | list:
    content = await _session_get(f'{_FIPIRAN}{path}', params=params)
    if json_resp is True:
        return loads(content)
    return content.decode().translate(_YK)
