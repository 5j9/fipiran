__version__ = '0.9.1.dev0'

from httpx import Client as _Client

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
_client = _Client()
_get = _client.get


def _api(path) -> dict | list:
    return _get(_API + path).json()


def _fipiran(path: str, params=None, json_resp=False) -> str | dict | list:
    r = _get(f'{_FIPIRAN}{path}', params=params)
    if json_resp is True:
        return r.json()
    return r.content.decode().translate(_YK)
