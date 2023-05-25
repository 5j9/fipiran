__version__ = '0.15.1.dev0'
from json import loads
from warnings import warn as _warn

from aiohttp import (
    ClientSession as _ClientSession,
    ClientTimeout as _ClientTimeout,
)

# noinspection PyUnresolvedReferences
from jdatetime import datetime as _jdatetime

# noinspection PyUnresolvedReferences
from pandas import (
    DataFrame as _DataFrame,
    read_html as _read_html,
    to_datetime as _to_datetime,
)

_FIPIRAN = 'https://www.fipiran.ir/'
_YK = ''.maketrans('يك', 'یک')
_API = 'https://fund.fipiran.ir/api/v1/'
SESSION : _ClientSession | None = None


class Session:

    def __new__(cls, *args, **kwargs) -> _ClientSession:
        global SESSION
        if 'timeout' not in kwargs:
            kwargs['timeout'] = _ClientTimeout(
                total=60., sock_connect=30., sock_read=30.)
        SESSION = _ClientSession(**kwargs)
        return SESSION


async def _read(url, **kwargs) -> bytes:
    r = await SESSION.get(url, **kwargs)
    if r.history:
        _warn(f'r.history is not empty (possible redirection): {r.history}')
    return await r.read()


async def _api(path) -> dict | list:
    return loads(await _read(_API + path))


async def _fipiran(path: str, params=None, json_resp=False) -> str | dict | list:
    content = await _read(f'{_FIPIRAN}{path}', params=params)
    if json_resp is True:
        return loads(content)
    return content.decode().translate(_YK)
