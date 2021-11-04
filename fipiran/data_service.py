from pandas import read_html as _read_html, DataFrame as _DataFrame
from typing import TypedDict as _TypedDict

from . import _fipiran, _to_jdate


def mutual_fund_list() -> _DataFrame:
    """Also see fipiran.fund.funds function."""
    return _read_html(_fipiran('DataService/ExportMFList'))[0]


def auto_complete_fund(id_: str) -> list[
    _TypedDict('FundAutoComplete', {'RegNo': int, 'Name': str})
]:
    return _fipiran('DataService/AutoCompletefund', (('id', id_),), True)


def mutual_fund_data(
    fund_name: str, reg_no: int, start_date: str, end_date: str
) -> _DataFrame:
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
    df = _read_html(xls)[0]
    df['Date'] = df['Date'].apply(_to_jdate)
    df['AghazFaliat'] = df['AghazFaliat'].apply(_to_jdate)
    return df
