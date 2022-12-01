from re import compile as _rc
from functools import partial as _partial
from . import _DataFrame, _fipiran, _read_html


_parenthesis_to_negative = _partial(_rc(r'\((\d+)\)').sub, r'-\1')


async def financial_ratios() -> _DataFrame:
    text = await _fipiran('Codal/Ratio')
    return _read_html(text)[0]


async def profit_growth() -> _DataFrame:
    text = await _fipiran('Codal/RoshdPos')
    return _read_html(_parenthesis_to_negative(text))[0]


async def profit_decline() -> _DataFrame:
    text = await _fipiran('Codal/RoshdNeg')
    return _read_html(_parenthesis_to_negative(text))[0]
