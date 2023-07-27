from pandas import NA as _NA

from fipiran import _api, _DataFrame, _to_datetime

_KNOWN_DTYPES = {
    # 'initiationDate': 'datetime64', fails on some funds
    'alpha': 'float64',
    'annualEfficiency': 'float64',
    'auditor': 'string',
    'beta': 'float64',
    'cancelNav': 'float64',
    'custodian': 'string',
    'dailyEfficiency': 'float64',
    # date cannot be set using astype, see:
    # https://github.com/pandas-dev/pandas/issues/53127
    'date': 'O',
    'dividendIntervalPeriod': 'Int64',
    'efficiency': 'float64',
    'fundSize': 'Int64',
    'fundType': 'int64',
    'guarantor': 'string',
    'guarantorSeoRegisterNo': 'Int64',
    'initiationDate': 'O',
    'insCode': 'string',
    'investedUnits': 'Int64',
    'issueNav': 'float64',
    'manager': 'string',
    'managerSeoRegisterNo': 'Int64',
    'monthlyEfficiency': 'float64',
    'name': 'string',
    'netAsset': 'Int64',
    'quarterlyEfficiency': 'float64',
    'rankLastUpdate': 'O',
    'rankOf12Month': 'float64',
    'rankOf24Month': 'float64',
    'rankOf36Month': 'float64',
    'rankOf48Month': 'float64',
    'rankOf60Month': 'float64',
    'regNo': 'int64',
    'sixMonthEfficiency': 'float64',
    'smallSymbolName': 'string',
    'statisticalNav': 'float64',
    'tempGuarantorName': 'string',
    'tempManagerName': 'string',
    'typeOfInvest': 'category',
    'weeklyEfficiency': 'float64',
}


class Fund:
    __slots__ = 'reg_no'

    def __init__(self, reg_no: int | str):
        self.reg_no = reg_no

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r})'

    async def asset_allocation_history(self) -> _DataFrame:
        """Return a dict where values are percentage of each kind of asset."""
        j = await _api(f'chart/portfoliochart?regno={self.reg_no}')
        df = _DataFrame(j)
        df['date'] = _to_datetime(df['date'], format='ISO8601')
        return df

    async def issue_cancel_history(self, /, *, all_=True) -> _DataFrame:
        j = await _api(
            f'chart/getfundchart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def nav_history(self, /, *, all_=True) -> _DataFrame:
        j = await _api(
            f'chart/getfundnetassetchart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def alpha_beta(self, /, *, all_=True) -> _DataFrame:
        j = await _api(
            f'chart/alphabetachart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def info(self) -> dict:
        return (await _api(f'fund/getfund?regno={self.reg_no}'))['item']


def _fix_website_address(df: _DataFrame):
    # assert df['websiteAddress'].map(len).max() == 1
    df['websiteAddress'] = (
        df['websiteAddress']
        .map(lambda lst: lst[0] if lst else _NA)
        .astype('string')
    )


def _apply_types(df: _DataFrame) -> _DataFrame:
    col_names = df.columns
    return df.astype(
        {cn: _KNOWN_DTYPES[cn] for cn in col_names if cn in _KNOWN_DTYPES},
        copy=False,
    )


async def funds() -> _DataFrame:
    """Return the data available at https://fund.fipiran.ir/mf/list.

    Also see fipiran.data_service.mutual_fund_list function.
    """
    j = await _api('fund/fundcompare')
    df = _apply_types(_DataFrame(j['items'], copy=False))
    df['date'] = _to_datetime(df['date'], format='ISO8601')
    _fix_website_address(df)
    return df


async def average_returns() -> _DataFrame:
    """Return a Dataframe for https://fund.fipiran.ir/mf/efficiency."""
    j = await _api('fund/averagereturns')
    df = _DataFrame(j, copy=False)
    return df.astype({'netAsset': 'Int64'}, copy=False)


async def map_data() -> _DataFrame:
    j = await _api('fund/treemap')
    df = _apply_types(_DataFrame(j['items'], copy=False))
    df['date'] = _to_datetime(df['date'], format='ISO8601')
    _fix_website_address(df)
    return df


async def dependency_graph_data() -> _DataFrame:
    j = await _api('fund/dependencygraph')
    df = _apply_types(_DataFrame(j['items'], copy=False))
    df['date'] = _to_datetime(df['date'], format='ISO8601')
    return df
