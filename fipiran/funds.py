from . import _api, _fipiran, _DataFrame, _read_html, _to_datetime


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
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def nav_history(self) -> _DataFrame:
        j = _api(f'chart/getfundnetassetchart?regno={self.reg_no}')
        df = _DataFrame(j, copy=False)
        df['date'] = _to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def info(self):
        return _api(f'fund/getfund?regno={self.reg_no}')['item']


def funds() -> _DataFrame:
    """Return the data available at https://fund.fipiran.ir/mf/list.

    Also see fipiran.data_service.mutual_fund_list function.
    """
    df = _DataFrame(_api('fund/fundcompare')['items'], copy=False).astype(
        {
            'regNo': 'int64',
            'name': 'string',
            'manager': 'string',
            'auditor': 'string',
            'custodian': 'string',
            'guarantor': 'string',
            'date': 'datetime64',
            'typeOfInvest': 'category',
        },
        copy=False,
    )
    return df


def average_returns() -> _DataFrame:
    return _read_html(_fipiran('Fund/MFBazdehAVG'))[0]


def map_data() -> _DataFrame:
    return _DataFrame(_api('fund/treemap')['items'], copy=False).astype(
        {
            'regNo': 'int64',
            'name': 'string',
            'typeOfInvest': 'category',
            'initiationDate': 'datetime64',
            'date': 'datetime64',
            'manager': 'string',
            'auditor': 'string',
            'custodian': 'string',
            'guarantor': 'string',
        },
        copy=False,
    )


def dependency_graph_data() -> _DataFrame:
    return _DataFrame(_api('fund/dependencygraph')['items'], copy=False).astype(
        {
            'regNo': 'int64',
            'name': 'string',
            'date': 'datetime64',
            'manager': 'string',
            'managerCode': 'string',
            'guarantor': 'string',
            'guarantorCode': 'string',
            # 'rankLastUpdate': 'datetime64',
            'typeOfInvest': 'category',
            'initiationDate': 'datetime64',
        },
        copy=False,
    )
