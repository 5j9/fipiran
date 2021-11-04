__version__ = '0.4.1.dev0'

from typing import TypedDict as _TypedDict
from functools import partial as _partial

from jdatetime import datetime as _jdatetime
from pandas import NA as _NA
from requests import get as _get


_FIPIRAN = 'https://www.fipiran.com/'
_YK = ''.maketrans('يك', 'یک')
_API = 'https://fund.fipiran.ir/api/v1/'


def _api(path) -> dict | list:
    return _get(_API + path).json()


def _fipiran(path: str, data=None, json_resp=False) -> str | dict | list:
    resp = _get(f'{_FIPIRAN}{path}', data)
    if json_resp is True:
        return resp.json()
    return resp.content.decode().translate(_YK)


_parse_jdate = _partial(_jdatetime.strptime, format='%Y/%m/%d')


def _to_jdate(s: str):
    try:
        return _parse_jdate(s)
    except ValueError:
        return _NA


def search(term) -> list[
    _TypedDict('AutoComplete', {'LVal18AFC': str, 'LSoc30': str})
]:
    return _fipiran('Home/AutoComplete', (('term', term),), True)
