from warnings import warn as _warn

from pandas import NA as _NA, DataFrame as _Df, to_datetime as _tdt

from fipiran import _api

_str = 'string'
_KNOWN_DTYPES = {
    # 'initiationDate': 'datetime64', fails on some funds
    'alpha': 'float64',
    'annualEfficiency': 'float64',
    'auditor': _str,
    'beta': 'float64',
    'cancelNav': 'float64',
    'custodian': _str,
    'dailyEfficiency': 'float64',
    # date cannot be set using astype, see:
    # https://github.com/pandas-dev/pandas/issues/53127
    'date': 'O',
    'dividendIntervalPeriod': 'Int64',
    'efficiency': 'float64',
    'fundSize': 'Int64',
    'fundType': 'int64',
    'guarantor': _str,
    'guarantorSeoRegisterNo': 'Int64',
    'initiationDate': 'O',
    'insCode': _str,
    'investedUnits': 'Int64',
    'issueNav': 'float64',
    'manager': _str,
    'managerSeoRegisterNo': 'Int64',
    'monthlyEfficiency': 'float64',
    'name': _str,
    'netAsset': 'Int64',
    'quarterlyEfficiency': 'float64',
    'rankLastUpdate': 'O',
    'rankOf12Month': 'float64',
    'rankOf24Month': 'float64',
    'rankOf36Month': 'float64',
    'rankOf48Month': 'float64',
    'rankOf60Month': 'float64',
    'regNo': _str,
    'sixMonthEfficiency': 'float64',
    'smallSymbolName': _str,
    'statisticalNav': 'float64',
    'tempGuarantorName': _str,
    'tempManagerName': _str,
    'typeOfInvest': 'category',
    'weeklyEfficiency': 'float64',
}


class Fund:
    __slots__ = 'reg_no'

    def __init__(self, reg_no: int | str):
        self.reg_no = reg_no

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r})'

    async def asset_allocation_history(self) -> _Df:
        """Return a dict where values are percentage of each kind of asset."""
        j = await _api(f'chart/portfoliochart?regno={self.reg_no}')
        df = _Df(j)
        df['date'] = _tdt(df['date'], format='ISO8601')
        return df

    async def navps_history(self, /, *, all_=True) -> _Df:
        j = await _api(
            f'chart/getfundchart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _Df(j, copy=False)
        df['date'] = _tdt(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def issue_cancel_history(self, /, *, all_=True) -> _Df:
        _warn(
            '`issue_cancel_history` is deprecated, use `navps_history` instead',
            DeprecationWarning,
        )
        return await self.navps_history(all_=all_)

    async def nav_history(self, /, *, all_=True) -> _Df:
        j = await _api(
            f'chart/getfundnetassetchart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _Df(j, copy=False)
        df['date'] = _tdt(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def alpha_beta(self, /, *, all_=True) -> _Df:
        j = await _api(
            f'chart/alphabetachart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _Df(j, copy=False)
        df['date'] = _tdt(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def info(self) -> dict:
        return (await _api(f'fund/getfund?regno={self.reg_no}'))['item']


def _fix_website_address(df: _Df):
    # assert df['websiteAddress'].map(len).max() == 1
    df['websiteAddress'] = df['websiteAddress'].map(
        lambda lst: lst[0] if lst else _NA
    )


def _apply_types(df: _Df) -> _Df:
    col_names = df.columns
    return df.astype(
        {cn: _KNOWN_DTYPES[cn] for cn in col_names if cn in _KNOWN_DTYPES},
        copy=False,
    )


async def funds() -> _Df:
    """Return the data available at https://fund.fipiran.ir/mf/list.

    Also see fipiran.data_service.mutual_fund_list function.
    """
    j = await _api('fund/fundcompare')
    df = _apply_types(_Df(j['items'], copy=False))
    df['date'] = _tdt(df['date'], format='ISO8601')
    _fix_website_address(df)
    return df


async def fund_types() -> _Df:
    j = await _api('fund/fundtype')
    return _Df(j['items'], copy=False)


async def average_returns() -> _Df:
    """Return a Dataframe for https://fund.fipiran.ir/mf/efficiency."""
    j = await _api('fund/averagereturns')
    df = _Df(j, copy=False)
    return df.astype({'netAsset': 'Int64'}, copy=False)


async def map_data() -> _Df:
    j = await _api('fund/treemap')
    df = _apply_types(_Df(j['items'], copy=False))
    df['date'] = _tdt(df['date'], format='ISO8601')
    _fix_website_address(df)
    return df


async def dependency_graph_data() -> _Df:
    j = await _api('fund/dependencygraph')
    df = _apply_types(_Df(j['items'], copy=False))
    df['date'] = _tdt(df['date'], format='ISO8601')
    return df
