__version__ = '0.23.2.dev0'

from json import JSONDecodeError as _JSONDecodeError, loads as _jl
from logging import error as _error
from typing import Any as _Any, overload as _overload

from aiohutils.session import SessionManager
from pandas import options as _o
from pydantic import BaseModel as _BaseModel

_o.mode.copy_on_write = True
_o.future.infer_string = True  # type: ignore

_FIPIRAN = 'https://www.fipiran.ir/'
_YK = ''.maketrans('يك', 'یک')
_API = 'https://www.fipiran.ir/services/'


session_manager = SessionManager(
    headers={
        'Referer': _FIPIRAN,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0',
    },
)


async def _read(url, **kwargs) -> bytes:
    r = await session_manager.get(url, **kwargs)
    return await r.read()


# todo: make model required
@_overload
async def _api(path, *, model: None = None, **kwargs) -> _Any: ...
@_overload
async def _api[T: _BaseModel](path, *, model: type[T], **kwargs) -> T: ...
async def _api(path, *, model: type[_BaseModel] | None = None, **kwargs):
    r = await _read(_API + path, **kwargs)
    if model is None:
        try:
            return _jl(r)
        except _JSONDecodeError:
            _error(f'{r = }')
            raise
    return model.model_validate_json(r)


async def _fipiran(path: str, params=None, json_resp=False) -> _Any:
    text = (
        (await _read(f'{_FIPIRAN}{path}', params=params))
        .decode()
        .translate(_YK)
    )
    if json_resp is True:
        return _jl(text)
    return text
