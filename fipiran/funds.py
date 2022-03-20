from . import _api, _fipiran, _DataFrame, _read_html, _to_datetime


class Fund:
    __slots__ = 'reg_no'

    def __init__(self, reg_no: int | str):
        self.reg_no = reg_no

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r})'

    async def asset_allocation(self) -> dict:
        """Return a dict where values are percentage of each kind of asset."""
        return await _api(f'chart/getfundchartasset?regno={self.reg_no}')

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
        j = await _api(f'chart/alphabeta?regno={self.reg_no}&showAll={str(all_).lower()}')
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    async def info(self) -> dict:
        return (await _api(f'fund/getfund?regno={self.reg_no}'))['item']

    async def top_units(self) -> _DataFrame:
        j = await _api(f'chart/fundtopunits?regno={self.reg_no}')
        df = _DataFrame(j, copy=False)
        return df


async def funds() -> _DataFrame:
    """Return the data available at https://fund.fipiran.ir/mf/list.

    Also see fipiran.data_service.mutual_fund_list function.
    """
    j = await _api('fund/fundcompare')
    df = _DataFrame(j['items'], copy=False).astype(
        {
            'regNo': 'int64',
            'name': 'string',
            'manager': 'string',
            'managerSeoRegisterNo': 'Int64',
            'auditor': 'string',
            'custodian': 'string',
            'guarantor': 'string',
            'date': 'datetime64',
            'typeOfInvest': 'category',
        },
        copy=False,
    )
    return df


async def average_returns() -> _DataFrame:
    return _read_html(await _fipiran('Fund/MFBazdehAVG'))[0]


async def map_data() -> _DataFrame:
    j = await _api('fund/treemap')
    return _DataFrame(j['items'], copy=False).astype(
        {
            'regNo': 'int64',
            'name': 'string',
            'typeOfInvest': 'category',
            'initiationDate': 'datetime64',
            'date': 'datetime64',
            'manager': 'string',
            'managerSeoRegisterNo': 'Int64',
            'auditor': 'string',
            'custodian': 'string',
            'guarantor': 'string',
        },
        copy=False,
    )


async def dependency_graph_data() -> _DataFrame:
    j = await _api('fund/dependencygraph')
    return _DataFrame(j['items'], copy=False).astype(
        {
            'regNo': 'int64',
            'name': 'string',
            'date': 'datetime64',
            'guarantor': 'string',
            'guarantorCode': 'string',
            # 'rankLastUpdate': 'datetime64',
            'typeOfInvest': 'category',
            'initiationDate': 'datetime64',
            'rankLastUpdate': 'datetime64',
        },
        copy=False,
    )
