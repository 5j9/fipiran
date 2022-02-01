from typing import TypedDict as _TypedDict

from . import _fipiran, _DataFrame, _read_html, _to_datetime, _jdatetime


_jstrptime = _jdatetime.strptime


def mutual_fund_list() -> _DataFrame:
    """Also see fipiran.fund.funds function."""
    return _read_html(_fipiran('DataService/ExportMFList'))[0]


def auto_complete_fund(id_: str) -> list[
    _TypedDict('FundAutoComplete', {'RegNo': int, 'Name': str})
]:
    return _fipiran('DataService/AutoCompletefund', (('id', id_),), True)


def mutual_fund_data(
    name: str, start_date: str, end_date: str,
    reg_no: int = None
) -> _DataFrame:
    """Return history of NAV, units, issue, and cancel.

    There various functions in this library to retrieve `reg_no`. If you
        want the names and numbers for all funds, you can use
        `mutual_fund_list`, but if only a single fund is desired the
        `auto_complete_fund` function can be used.
    `reg_no` is optional and if left out then the first result of
        `auto_complete_fund` will be used.

    Date parameters should be strings representing SH dates e.g.:
        '1394/01/01'
    """
    if reg_no is None:
        d = auto_complete_fund(name)[0]
        reg_no = d['RegNo']
        name = d['Name']
    xls = _fipiran('DataService/ExportMF', (
        ('Mutualpara', name),
        ('RegNoN', reg_no),
        ('MFStart', start_date),
        ('MFEnd', end_date)))
    df = _read_html(xls)[0]
    df['Date'] = df['Date'].apply(_jstrptime, args=('%Y/%m/%d',))
    df['AghazFaliat'] = df['AghazFaliat'].apply(_jstrptime, args=('%Y/%m/%d',))
    return df


def auto_complete_index(id_: str) -> list[
    _TypedDict('IndexAutoComplete', {'LVal30': str, 'InstrumentID': str})
]:
    return _fipiran('DataService/AutoCompleteindex', (('id', id_),), True)


def export_index(
    lval30: str, start_date: str | int, end_date: str | int,
    instrument_id: str = None
) -> _DataFrame:
    """Return history of requested index.

    Use the `auto_complete_index` function to retrieve lval30 and instrument_id
        of the desired index.
    `instrument_id` is optional and if left out then the first result of
        `auto_complete_symbol` will be used.
    Date parameters should be SH dates in YYYYMMDD format e.g.:
        '13940101'
    """
    if instrument_id is None:
        d = auto_complete_index(lval30)[0]
        lval30 = d['LVal30']
        instrument_id = d['InstrumentID']
    xls = _fipiran('DataService/ExportIndex', (
        ('indexpara', lval30),
        ('inscodeindex', instrument_id),
        ('indexStart', start_date),
        ('indexEnd', end_date)))
    df = _read_html(xls)[0]
    df['dateissue'] = df['dateissue'].apply(str).apply(_jstrptime, args=('%Y%m%d',))
    return df


def auto_complete_symbol(id_: str) -> list[
    _TypedDict('SymbolAutoComplete', {'LVal18AFC': str, 'InstrumentID': str})
]:
    return _fipiran('DataService/AutoCompletesymbol', (('id', id_),), True)


def export_symbol(
    lval18afc: str, start_date: str | int, end_date: str | int,
    instrument_id: str = None
) -> _DataFrame:
    """Return history of requested index.

    Use the `auto_complete_symbol` function to retrieve `lval18afc` and
        `instrument_id` of the desired symbol.
    `instrument_id` is optional and if left out then the first result of
        `auto_complete_symbol` will be used.

    Date parameters should be SH dates in YYYYMMDD format e.g.:
        '13940101'
    """
    if instrument_id is None:
        d = auto_complete_symbol(lval18afc)[0]
        lval18afc = d['LVal18AFC']
        instrument_id = d['InstrumentID']
    xls = _fipiran('DataService/Exportsymbol', (
        ('symboldatapara', lval18afc),
        ('inscodesymbol', instrument_id),
        ('symbolStart', start_date),
        ('symbolEnd', end_date)))
    df = _read_html(xls)[0]
    df['PDate'] = df['PDate'].apply(str).apply(_jstrptime, args=('%Y%m%d',))
    df['GDate'] = _to_datetime(df['GDate'], format='%Y%m%d')
    return df
