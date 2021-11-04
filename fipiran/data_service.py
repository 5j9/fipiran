from typing import TypedDict as _TypedDict

from jdatetime import datetime as _jdatetime
import pandas as _pd

from . import _fipiran


_jstrptime = _jdatetime.strptime


def mutual_fund_list() -> _pd.DataFrame:
    """Also see fipiran.fund.funds function."""
    return _pd.read_html(_fipiran('DataService/ExportMFList'))[0]


def auto_complete_fund(id_: str) -> list[
    _TypedDict('FundAutoComplete', {'RegNo': int, 'Name': str})
]:
    return _fipiran('DataService/AutoCompletefund', (('id', id_),), True)


def mutual_fund_data(
    fund_name: str, reg_no: int, start_date: str, end_date: str
) -> _pd.DataFrame:
    """Return history of NAV, units, issue, and cancel.

    There various functions in this library to retrieve `reg_no`. If you
    want the names and numbers for all funds, you can use `mutual_fund_list`,
    but if only a single fund is desired the `auto_complete_fund` function
    can be used.
    Date parameters should be strings representing SH dates e.g.:
        '1394/01/01'
    """
    xls = _fipiran('DataService/ExportMF', (
        ('Mutualpara', fund_name),
        ('RegNoN', reg_no),
        ('MFStart', start_date),
        ('MFEnd', end_date)))
    df = _pd.read_html(xls)[0]
    df['Date'] = df['Date'].apply(_jstrptime, args=('%Y/%m/%d',))
    df['AghazFaliat'] = df['AghazFaliat'].apply(_jstrptime, args=('%Y/%m/%d',))
    return df


def auto_complete_index(id_: str) -> list[
    _TypedDict('IndexAutoComplete', {'LVal30': str, 'InstrumentID': str})
]:
    return _fipiran('DataService/AutoCompleteindex', (('id', id_),), True)


def export_index(
    lval30: str, instrument_id: str, start_date: str | int, end_date: str | int
) -> _pd.DataFrame:
    """Return history of requested index.

    Use the `auto_complete_index` function to retrieve lval30 and instrument_id
        of the desired index.
    Date parameters should be SH dates in YYYYMMDD format e.g.:
        '13940101'
    """
    xls = _fipiran('DataService/ExportIndex', (
        ('indexpara', lval30),
        ('inscodeindex', instrument_id),
        ('indexStart', start_date),
        ('indexEnd', end_date)))
    df = _pd.read_html(xls)[0]
    df['dateissue'] = df['dateissue'].apply(str).apply(_jstrptime, args=('%Y%m%d',))
    return df


def auto_complete_symbol(id_: str) -> list[
    _TypedDict('SymbolAutoComplete', {'LVal18AFC': str, 'InstrumentID': str})
]:
    return _fipiran('DataService/AutoCompletesymbol', (('id', id_),), True)


def export_symbol(
    lval18afc: str, instrument_id: str, start_date: str | int, end_date: str | int
) -> _pd.DataFrame:
    """Return history of requested index.

    Use the `auto_complete_symbol` function to retrieve `lval18afc` and
        `instrument_id` of the desired symbol.
    Date parameters should be SH dates in YYYYMMDD format e.g.:
        '13940101'
    """
    xls = _fipiran('DataService/Exportsymbol', (
        ('symboldatapara', lval18afc),
        ('inscodesymbol', instrument_id),
        ('symbolStart', start_date),
        ('symbolEnd', end_date)))
    df = _pd.read_html(xls)[0]
    df['PDate'] = df['PDate'].apply(str).apply(_jstrptime, args=('%Y%m%d',))
    df['GDate'] = _pd.to_datetime(df['GDate'], format='%Y%m%d')
    return df
