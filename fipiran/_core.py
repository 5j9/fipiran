from requests import get
from pandas import DataFrame, to_datetime


API = 'https://fund.fipiran.ir/api/v1/'


class FundProfile:
    __slots__ = 'reg_no'

    def __init__(self, reg_no: int | str):
        self.reg_no = reg_no

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r})'

    def asset_allocation(self) -> dict:
        """Return a dict where values are percentage of each kind of asset."""
        return api(f'chart/getfundchartasset?regno={self.reg_no}')

    def issue_cancel_history(self) -> DataFrame:
        j = api(f'chart/getfundchart?regno={self.reg_no}')
        df = DataFrame(j)
        df['date'] = to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def nav_history(self) -> DataFrame:
        j = api(f'chart/getfundnetassetchart?regno={self.reg_no}')
        df = DataFrame(j)
        df['date'] = to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    def info(self):
        return api(f'fund/getfund?regno={self.reg_no}')['item']


def api(path) -> dict | list:
    return get(API + path).json()


def funds() -> DataFrame:
    return DataFrame(api('fund/fundlist')['items'])


def search(term) -> list[dict]:
    return get(
        'https://www.fipiran.com/Home/AutoComplete', data=(('term', term),)
    ).json()
