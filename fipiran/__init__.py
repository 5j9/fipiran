__version__ = '0.9.1.dev0'

from json import loads
from functools import partial as _partial

from urllib3 import PoolManager as _PoolManager, Timeout as _Timeout

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
_http = _PoolManager(timeout=_Timeout(total=15., connect=5., read=5.))
_http_get: _http.request = _partial(_http.request, 'GET')


def _api(path) -> dict | list:
    return loads(_http_get(_API + path).data)


def _fipiran(path: str, fields=None, json_resp=False) -> str | dict | list:
    data = _http_get(f'{_FIPIRAN}{path}', fields).data
    if json_resp is True:
        return loads(data)
    return data.decode().translate(_YK)
