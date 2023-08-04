from functools import partial as _partial
from re import compile as _rc

from pandas import DataFrame as _Df, read_html as _rh

from . import _fipiran

_parenthesis_to_negative = _partial(_rc(r'\((\d+)\)').sub, r'-\1')


async def financial_ratios() -> _Df:
    text = await _fipiran('Codal/Ratio')
    return _rh(text)[0]


async def profit_growth() -> _Df:
    text = await _fipiran('Codal/RoshdPos')
    return _rh(_parenthesis_to_negative(text))[0]


async def profit_decline() -> _Df:
    text = await _fipiran('Codal/RoshdNeg')
    return _rh(_parenthesis_to_negative(text))[0]
