from __future__ import annotations

from functools import partial
from typing import Literal

from requests import get
from pandas import DataFrame, to_datetime, read_html
from bs4 import BeautifulSoup
from jdatetime import datetime as jdatetime


API = 'https://fund.fipiran.ir/api/v1/'
FIPIRAN = 'https://www.fipiran.com/'
YK = ''.maketrans('يك', 'یک')


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


class Symbol:
    __slots__ = 'inscode', 'name'

    def __init__(self, inscode: int | str, name: str):
        """Use `from_name` or `from_inscode` if only 1 parameter is known."""
        self.inscode = inscode
        self.name = name

    def __repr__(self):
        return f'{type(self).__name__}({self.inscode!r}, {self.name!r})'

    @staticmethod
    def from_name(symbolpara: str, /) -> Symbol:
        text = fipiran(f'Symbol?symbolpara={symbolpara}')
        start = text.find("'inscode': '") + 12
        end = text.find("'", start)
        inscode = int(text[start: end])
        start = text.find("var symbolpara = '") + 18
        end = text.find("'", start)
        name = text[start: end]
        return Symbol(inscode, name)

    def price_data(self) -> dict:
        # note: some fields like Trailing P/E and Forward P/E are *currently*
        # not computed by fipiran and are always empty.
        text = fipiran(f'Symbol/_priceData?inscode={self.inscode}')
        bs = soup(text)
        so = bs.select_one
        d = {}

        def num(s: str) -> float:
            s = s.replace(',', '').strip(' ')
            if s[0] == '(':  # negative value
                return -float(s.strip('()'))
            return float(s)

        for k in (  # numerical values
            'PriceMin', 'PriceMax', 'PDrCotVal', 'PriceFirst',
            'PClosing', 'changepdr', 'changepc', 'prevPrice', 'ZTotTran',
            'QTotTran5J', 'QTotCap'
        ):
            d[k] = num(so(f'#{k}').text)

        d['Deven'] = jdatetime.strptime(so('#Deven').text, '%Y/%m/%d-%H:%M:%S')

        tmin, tmax = bs.find(string='قیمت مجاز').next.text.split(' - ')
        d['tmin'] = num(tmin)
        d['tmax'] = num(tmax)

        return d

    def best_limit_data(self) -> list[DataFrame]:
        text = fipiran(f'Symbol/_BestLimitData?inscode={self.inscode}')
        return read_html(text)

    def refrence_data(self) -> dict:
        text = fipiran(f'Symbol/_RefrenceData?symbolpara={self.name}')
        bs = soup(text)
        h4s = [i.text.strip(': ') for i in bs.select('h4')]
        spans = [i.text for i in bs.select('span')]
        d = dict(zip(h4s, spans))
        # e.g. 'کد معاملاتی نماد', 'IRO1MSMI0001'
        k, v = bs.select_one('span')['title'].split(' :')
        d[k] = v
        return d

    def statistic(self, days: Literal[365, 180, 90, 30, 7]) -> DataFrame:
        return read_html(
            fipiran(f'Symbol/statistic{days}?inscode={self.inscode}'))[0]


soup = partial(BeautifulSoup, features='lxml')


def fipiran(path: str) -> str:
    return get(f'{FIPIRAN}{path}').content.decode().translate(YK)


def api(path) -> dict | list:
    return get(API + path).json()


def funds() -> DataFrame:
    return DataFrame(api('fund/fundlist')['items'])


def search(term) -> list[dict]:
    return get(FIPIRAN + 'Home/AutoComplete', data=(('term', term),)).json()
