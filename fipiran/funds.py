from pandas import NA as _NA

from . import _api, _DataFrame, _to_datetime

_COMMON_DTYPES = {
    'guarantor': 'string',
    # 'initiationDate': 'datetime64', fails on some funds
    'manager': 'string',
    'name': 'string',
    'regNo': 'int64',
    'statisticalNav': 'float64',
    'typeOfInvest': 'category',
}
_FUND_DTYPES = _COMMON_DTYPES | {
    'auditor': 'string',
    'custodian': 'string',
    'dividendIntervalPeriod': 'Int64',
    'guarantorSeoRegisterNo': 'Int64',
    'managerSeoRegisterNo': 'Int64',
}
_GRAPH_DTYPES = _COMMON_DTYPES | {
    'fundSize': 'Int64',
    'netAsset': 'Int64',
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
        j = await _api(f'chart/getfundchart?regno={self.reg_no}&showAll={str(all_).lower()}')
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def nav_history(self, /, *, all_=True) -> _DataFrame:
        j = await _api(f'chart/getfundnetassetchart?regno={self.reg_no}&showAll={str(all_).lower()}')
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def alpha_beta(self, /, *, all_=True) -> _DataFrame:
        j = await _api(f'chart/alphabetachart?regno={self.reg_no}&showAll={str(all_).lower()}')
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def info(self) -> dict:
        return (await _api(f'fund/getfund?regno={self.reg_no}'))['item']


async def funds() -> _DataFrame:
    """Return the data available at https://fund.fipiran.ir/mf/list.

    Also see fipiran.data_service.mutual_fund_list function.
    """
    j = await _api('fund/fundcompare')
    df = _DataFrame(j['items'], copy=False).astype(_FUND_DTYPES, copy=False)
    df['date'] = _to_datetime(df['date'], format='ISO8601')
    assert df['websiteAddress'].map(len).max() == 1
    df['websiteAddress'] = df['websiteAddress'].map(
        lambda lst: lst[0] if lst else _NA
    ).astype('string')
    return df


async def average_returns() -> _DataFrame:
    """Return a Dataframe for https://fund.fipiran.ir/mf/efficiency."""
    j = await _api('fund/averagereturns')
    df = _DataFrame(j, copy=False)
    return df.astype({'netAsset': 'Int64'}, copy=False)


async def map_data() -> _DataFrame:
    j = await _api('fund/treemap')
    df = _DataFrame(j['items'], copy=False).astype(_FUND_DTYPES, copy=False)
    df['date'] = _to_datetime(df['date'], format='ISO8601')
    return df


async def dependency_graph_data() -> _DataFrame:
    j = await _api('fund/dependencygraph')
    df = _DataFrame(j['items'], copy=False).astype(_GRAPH_DTYPES, copy=False)
    df['date'] = _to_datetime(df['date'], format='ISO8601')
    return df
