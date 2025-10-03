__version__ = '0.23.2.dev0'

from json import loads as _jl
from typing import Any as _Any

from aiohutils.session import SessionManager
from pandas import options as _o
from pydantic import BaseModel as _BaseModel


class _LoosModel(_BaseModel, extra='allow'):
    pass


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


async def _api[T: _BaseModel](path, *, model: type[T], **kwargs) -> T:
    r = await _read(_API + path, **kwargs)
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
