from pandas import read_html as _read_html, DataFrame as _DataFrame

from . import _fipiran


def mutual_fund_list() -> _DataFrame:
    """Also see fipiran.fund.funds function."""
    return _read_html(_fipiran('DataService/ExportMFList'))[0]
