__version__ = '0.17.1.dev0'
from json import JSONDecodeError as _JSONDecodeError, loads
from logging import error as _error

from aiohutils.session import SessionManager

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


session_manger = SessionManager(
    kwargs={
        'headers': {
            'Referer': 'https://fund.fipiran.ir',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
        }
    }
)


async def _read(url, **kwargs) -> bytes:
    r = await session_manger.get(url, **kwargs)
    return await r.read()


async def _api(path) -> dict | list:
    r = await _read(_API + path)
    try:
        return loads(r)
    except _JSONDecodeError:
        _error(f'{r = }')
        raise


async def _fipiran(
    path: str, params=None, json_resp=False
) -> str | dict | list:
    content = await _read(f'{_FIPIRAN}{path}', params=params)
    if json_resp is True:
        return loads(content)
    return content.decode().translate(_YK)
