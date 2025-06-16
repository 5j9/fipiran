from functools import partial as _partial
from typing import TypedDict as _TypedDict

from aiohutils.pd import html_to_df as _hd
from jdatetime import datetime as _jdt
from pandas import DataFrame as _Df, to_datetime as _tdt

from . import _fipiran

_jstrptime = _jdt.strptime


class FundAutoComplete(_TypedDict):
    RegNo: int
    Name: str


async def auto_complete_fund(
    id_: str,
) -> list[FundAutoComplete]:
    return await _fipiran('DataService/AutoCompletefund', (('id', id_),), True)


class IndexAutoComplete(_TypedDict):
    LVal30: str
    InstrumentID: str


async def auto_complete_index(
    id_: str,
) -> list[IndexAutoComplete]:
    return await _fipiran(
        'DataService/AutoCompleteindex', (('id', id_),), True
    )


async def export_index(
    lval30: str,
    start_date: str | int,
    end_date: str | int,
    instrument_id: str | None = None,
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
    df = _hd(xls)
    df['dateissue'] = (
        df['dateissue'].astype(str).map(_partial(_jstrptime, format='%Y%m%d'))
    )
    return df


class SymbolAutoComplete(_TypedDict):
    LVal18AFC: str
    InstrumentID: str


async def auto_complete_symbol(
    id_: str,
) -> list[SymbolAutoComplete]:
    return await _fipiran(
        'DataService/AutoCompletesymbol', (('id', id_),), True
    )


async def export_symbol(
    lval18afc: str,
    start_date: str | int,
    end_date: str | int,
    instrument_id: str | None = None,
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
    df = _hd(xls)
    df['PDate'] = (
        df['PDate'].map(str).map(_partial(_jstrptime, format='%Y%m%d'))
    )
    df['GDate'] = _tdt(df['GDate'], format='%Y%m%d')
    return df


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
    df = _hd(xls)
    jdate_cols = ['PublishDate', 'FinanceYear']
    df[jdate_cols] = df[jdate_cols].map(str).map(_jstrptime, format='%Y/%m/%d')
    return df


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
    df = _hd(xls)
    jdate_cols = ['publishDate', 'FinanceYear']
    df[jdate_cols] = df[jdate_cols].map(str).map(_jstrptime, format='%Y/%m/%d')
    return df


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
    df = _hd(xls)
    jdate_cols = ['PublishDate', 'FinancialYear']
    df[jdate_cols] = df[jdate_cols].map(str).map(_jstrptime, format='%Y/%m/%d')
    return df
