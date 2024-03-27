from functools import partial as _partial
from re import compile as _rc

from aiohutils.df import from_html as _from_html
from polars import DataFrame as _Df

from . import _fipiran

_parenthesis_to_negative = _partial(_rc(r'\((\d+)\)').sub, r'-\1')


async def financial_ratios() -> _Df:
    text = await _fipiran('Codal/Ratio')
    return _from_html(text)


async def profit_growth() -> _Df:
    text = await _fipiran('Codal/RoshdPos')
    return _from_html(_parenthesis_to_negative(text))


async def profit_decline() -> _Df:
    text = await _fipiran('Codal/RoshdNeg')
    return _from_html(_parenthesis_to_negative(text))
