from warnings import warn as _warn

from polars import (
    Categorical as _Categorical,
    DataFrame as _Df,
    Float64 as _Float64,
    Int64 as _Int64,
)

from fipiran import _api

_KNOWN_DTYPES = {
    # 'initiationDate': 'datetime64', fails on some funds
    'alpha': _Float64,
    'annualEfficiency': _Float64,
    'beta': _Float64,
    'cancelNav': _Float64,
    'dailyEfficiency': _Float64,
    'dividendIntervalPeriod': _Int64,
    'efficiency': _Float64,
    'fundSize': _Int64,
    'fundType': _Int64,
    # 'guarantor': _String,
    'guarantorSeoRegisterNo': _Int64,
    # 'initiationDate': _Object,
    # 'insCode': _String,
    'investedUnits': _Int64,
    'issueNav': _Float64,
    # 'manager': _String,
    'managerSeoRegisterNo': _Int64,
    'monthlyEfficiency': _Float64,
    # 'name': _String,
    'netAsset': _Int64,
    'quarterlyEfficiency': _Float64,
    # 'rankLastUpdate': _Object,
    'rankOf12Month': _Float64,
    'rankOf24Month': _Float64,
    'rankOf36Month': _Float64,
    'rankOf48Month': _Float64,
    'rankOf60Month': _Float64,
    'regNo': _Int64,
    'sixMonthEfficiency': _Float64,
    # 'smallSymbolName': _String,
    'statisticalNav': _Float64,
    # 'tempGuarantorName': _String,
    # 'tempManagerName': _String,
    'typeOfInvest': _Categorical,
    'weeklyEfficiency': _Float64,
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
        return df.with_columns(df['date'].str.to_datetime())

    async def navps_history(self, /, *, all_=True) -> _Df:
        j = await _api(
            f'chart/getfundchart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _Df(j)
        return df.with_columns(df['date'].str.to_datetime())

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
        df = _Df(j)
        return df.with_columns(df['date'].str.to_datetime())

    async def alpha_beta(self, /, *, all_=True) -> _Df:
        j = await _api(
            f'chart/alphabetachart?regno={self.reg_no}&showAll={str(all_).lower()}'
        )
        df = _Df(j)
        return df.with_columns(df['date'].str.to_datetime())

    async def info(self) -> dict:
        return (await _api(f'fund/getfund?regno={self.reg_no}'))['item']


def _fix_website_address(df: _Df):
    # assert df['websiteAddress'].map(len).max() == 1
    df['websiteAddress'] = df['websiteAddress'].explode()


def _apply_types(df: _Df) -> _Df:
    col_names = df.columns
    return df.cast(
        {cn: _KNOWN_DTYPES[cn] for cn in col_names if cn in _KNOWN_DTYPES}
    )


async def funds() -> _Df:
    """Return the data available at https://fund.fipiran.ir/mf/list.

    Also see fipiran.data_service.mutual_fund_list function.
    """
    j = await _api('fund/fundcompare')
    df = _apply_types(_Df(j['items'], infer_schema_length=None))
    return df.with_columns(
        df['date'].str.to_datetime(), df['websiteAddress'].explode()
    )


async def average_returns() -> _Df:
    """Return a Dataframe for https://fund.fipiran.ir/mf/efficiency."""
    j = await _api('fund/averagereturns')
    df = _Df(j)
    return df.cast({'netAsset': _Int64})


async def map_data() -> _Df:
    j = await _api('fund/treemap')
    df = _apply_types(_Df(j['items'], infer_schema_length=None))
    df = df.with_columns(df['date'].str.to_datetime())
    return df.with_columns(df['websiteAddress'].explode())


async def dependency_graph_data() -> _Df:
    j = await _api('fund/dependencygraph')
    df = _apply_types(_Df(j['items']))
    return df.with_columns(df['date'].str.to_datetime())
