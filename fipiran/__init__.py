__version__ = '0.8.1.dev0'

from requests import get as _get

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


def _api(path) -> dict | list:
    return _get(_API + path).json()


def _fipiran(path: str, data=None, json_resp=False) -> str | dict | list:
    resp = _get(f'{_FIPIRAN}{path}', data)
    if json_resp is True:
        return resp.json()
    return resp.content.decode().translate(_YK)
