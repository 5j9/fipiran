from functools import partial as _partial
from typing import TypedDict as _TypedDict

from aiohutils.pd import from_html as _from_html
from jdatetime import datetime as _jdt
from polars import DataFrame as _Df, String as _String

from . import _fipiran

_jstrptime = _jdt.strptime


async def auto_complete_fund(
    id_: str,
) -> list[_TypedDict('FundAutoComplete', {'RegNo': int, 'Name': str})]:
    return await _fipiran('DataService/AutoCompletefund', (('id', id_),), True)


async def auto_complete_index(
    id_: str,
) -> list[
    _TypedDict('IndexAutoComplete', {'LVal30': str, 'InstrumentID': str})
]:
    return await _fipiran(
        'DataService/AutoCompleteindex', (('id', id_),), True
    )


async def export_index(
    lval30: str,
    start_date: str | int,
    end_date: str | int,
    instrument_id: str = None,
) -> _Df:
    """Return history of requested index.

    Use the `auto_complete_index` function to retrieve lval30 and instrument_id
        of the desired index.
    `instrument_id` is optional and if left out then the first result of
        `auto_complete_symbol` will be used.
    Date parameters should be SH dates in YYYYMMDD format e.g.:
        '13940101'
    """
    if instrument_id is None:
        d = (await auto_complete_index(lval30))[0]
        lval30 = d['LVal30']
        instrument_id = d['InstrumentID']
    xls = await _fipiran(
        'DataService/ExportIndex',
        (
            ('indexpara', lval30),
            ('inscodeindex', instrument_id),
            ('indexStart', start_date),
            ('indexEnd', end_date),
        ),
    )
    df = _from_html(xls)
    return df.with_columns(
        df['dateissue']
        .cast(_String)
        .map_elements(_partial(_jstrptime, format='%Y%m%d'))
    )


async def auto_complete_symbol(
    id_: str,
) -> list[
    _TypedDict('SymbolAutoComplete', {'LVal18AFC': str, 'InstrumentID': str})
]:
    return await _fipiran(
        'DataService/AutoCompletesymbol', (('id', id_),), True
    )


async def export_symbol(
    lval18afc: str,
    start_date: str | int,
    end_date: str | int,
    instrument_id: str = None,
) -> _Df:
    """Return history of requested index.

    Use the `auto_complete_symbol` function to retrieve `lval18afc` and
        `instrument_id` of the desired symbol.
    `instrument_id` is optional and if left out then the first result of
        `auto_complete_symbol` will be used.

    Date parameters should be SH dates in YYYYMMDD format e.g.:
        '13940101'
    """
    if instrument_id is None:
        d = (await auto_complete_symbol(lval18afc))[0]
        lval18afc = d['LVal18AFC']
        instrument_id = d['InstrumentID']
    xls = await _fipiran(
        'DataService/Exportsymbol',
        (
            ('symboldatapara', lval18afc),
            ('inscodesymbol', instrument_id),
            ('symbolStart', start_date),
            ('symbolEnd', end_date),
        ),
    )
    df = _from_html(xls)
    return df.with_columns(
        df['GDate'].cast(_String).str.to_datetime('%Y%m%d'),
    )


def _publish_date_finance_year(
    df: _Df, pub='PublishDate', fin='FinanceYear'
) -> _Df:
    return df.with_columns(
        df[pub].map_elements(_partial(_jstrptime, format='%Y/%m/%d')),
        df[fin].map_elements(_partial(_jstrptime, format='%Y/%m/%d')),
    )


async def balance_sheet(
    l18: str,
    year: str | int,
) -> _Df:
    """Return balance sheet for the requested symbol name as DataFrame.

    https://www.fipiran.ir/DataService/BSIndex
    """
    xls = await _fipiran(
        'DataService/ExportBS',
        (
            ('symbolparaBS', l18),
            ('year', year),
        ),
    )
    df = _from_html(xls)
    return _publish_date_finance_year(df)


async def profit_loss(
    l18: str,
    year: str | int,
) -> _Df:
    """Return profit and loss statements for the requested symbol and year.

    https://www.fipiran.ir/DataService/ISIndex
    """
    xls = await _fipiran(
        'DataService/ExportIS',
        (
            ('symbolparaIS', l18),
            ('year', year),
        ),
    )
    df = _from_html(xls)
    return _publish_date_finance_year(df, pub='publishDate')


async def financial_ratios(
    l18: str,
    year: str | int,
) -> _Df:
    """Return financial ratios for the requested symbol and year.

    https://www.fipiran.ir/DataService/RatioIndex
    """
    xls = await _fipiran(
        'DataService/ExportRatio',
        (
            ('symbolparaR', l18),
            ('year', year),
        ),
    )
    df = _from_html(xls)
    return _publish_date_finance_year(df, fin='FinancialYear')
