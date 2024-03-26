__version__ = '0.22.1.dev0'

from functools import partial
from json import JSONDecodeError as _JSONDecodeError, loads as _jl
from logging import error as _error

from aiohttp import TCPConnector
from aiohutils.session import SessionManager
from pandas import options as _o

_o.mode.copy_on_write = True
_o.future.infer_string = True

_FIPIRAN = 'https://www.fipiran.ir/'
_YK = ''.maketrans('يك', 'یک')
_API = 'https://fund.fipiran.ir/api/v1/'


session_manager = SessionManager(
    headers={
        'Referer': 'https://fund.fipiran.ir',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    },
    connector=partial(TCPConnector, force_close=True),
)


async def _read(url, **kwargs) -> bytes:
    r = await session_manager.get(url, **kwargs)
    return await r.read()


async def _api(path) -> dict | list:
    r = await _read(_API + path)
    try:
        return _jl(r)
    except _JSONDecodeError:
        _error(f'{r = }')
        raise


async def _fipiran(
    path: str, params=None, json_resp=False
) -> str | dict | list:
    content = await _read(f'{_FIPIRAN}{path}', params=params)
    if json_resp is True:
        return _jl(content)
    return content.decode().translate(_YK)
