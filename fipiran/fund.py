from functools import partial as _partial

from jdatetime import datetime as _jdatetime
from pandas import DataFrame as _DataFrame, to_datetime as _to_datetime, \
    read_html as _read_html, to_numeric as _to_numeric, NA as _NA
from . import _api, _fipiran


class Fund:
    __slots__ = 'reg_no'

    def __init__(self, reg_no: int | str):
        self.reg_no = reg_no

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r})'

    def asset_allocation(self) -> dict:
        """Return a dict where values are percentage of each kind of asset."""
        return _api(f'chart/getfundchartasset?regno={self.reg_no}')

    def issue_cancel_history(self) -> _DataFrame:
        j = _api(f'chart/getfundchart?regno={self.reg_no}')
        df = _DataFrame(j)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def nav_history(self) -> _DataFrame:
        j = _api(f'chart/getfundnetassetchart?regno={self.reg_no}')
        df = _DataFrame(j)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def info(self):
        return _api(f'fund/getfund?regno={self.reg_no}')['item']


def funds() -> _DataFrame:
    """Also see fipiran.data_service.mutual_fund_list function."""
    return _DataFrame(_api('fund/fundlist')['items'])


def average_returns() -> _DataFrame:
    return _read_html(_fipiran('Fund/MFBazdehAVG'))[0]


def ratings() -> _DataFrame:
    df = _read_html(_fipiran('Fund/Rating'))[0]
    # Cannot use iloc in LHS, see: https://stackoverflow.com/questions/52395179
    df[df.columns[1:4]] = df.iloc[:, 1:4].apply(_to_numeric, args=('coerce',))
    _parse_jdate = _partial(_jdatetime.strptime, format='%Y/%m/%d')

    def _jdate_na(s: str):
        try:
            return _parse_jdate(s)
        except ValueError:
            return _NA
    df.iloc[:, -1] = df.iloc[:, -1].apply(_jdate_na)
    return df
