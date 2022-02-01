from functools import partial as _partial
from typing import Literal as _Literal

from bs4 import BeautifulSoup as _BeautifulSoup

from . import _fipiran, _DataFrame, _read_html, _to_datetime, _jdatetime


_KY = ''.maketrans('کی', 'كي')


class Symbol:
    __slots__ = '_inscode', 'l18', 'l30', '_symbolpara'

    def __init__(self, l18: str, inscode: int | str = None):
        self.l18 = l18
        self._symbolpara = self.l18.translate(_KY)
        self._inscode = inscode

    def __repr__(self):
        return f'{type(self).__name__}({self.l18!r})'

    def __eq__(self, other):
        return isinstance(other, Symbol) and other.l18 == self.l18

    @property
    def inscode(self):
        if (inscode := getattr(self, '_inscode', None)) is not None:
            return inscode
        text = _fipiran(f'Symbol?symbolpara={self._symbolpara}')
        start = text.find("'inscode': '") + 12
        end = text.find("'", start)
        self._inscode = inscode = int(text[start: end])
        return inscode

    def price_data(self) -> dict:
        # note: some fields like Trailing P/E and Forward P/E are *currently*
        # not computed by fipiran and are always empty.
        text = _fipiran(f'Symbol/_priceData?inscode={self.inscode}')
        bs = _soup(text)
        so = bs.select_one
        d = {}

        def int_or_float(s: str) -> int | float:
            try:
                return int(s)
            except ValueError:
                return float(s)

        def num(s: str) -> int | float:
            s = s.replace(',', '').strip(' ')
            if s[0] == '(':  # negative value
                return -float(s.strip('()'))
            return int_or_float(s)

        for k in (  # numerical values
            'PriceMin', 'PriceMax', 'PDrCotVal', 'PriceFirst',
            'PClosing', 'changepdr', 'changepc', 'prevPrice', 'ZTotTran',
            'QTotTran5J', 'QTotCap'
        ):
            d[k] = num(so(f'#{k}').text)

        d['Deven'] = _jdatetime.strptime(so('#Deven').text, '%Y/%m/%d-%H:%M:%S')

        tmin, tmax = bs.find(string='قیمت مجاز').next.text.split(' - ')
        d['tmin'] = num(tmin)
        d['tmax'] = num(tmax)

        return d

    def best_limit_data(self) -> list[_DataFrame]:
        text = _fipiran(f'Symbol/_BestLimitData?inscode={self.inscode}')
        return _read_html(text)

    def reference_data(self) -> dict:
        text = _fipiran(f'Symbol/_RefrenceData?symbolpara={self._symbolpara}')
        bs = _soup(text)
        h4s = [i.text.strip(': ') for i in bs.select('h4')]
        spans = [i.text for i in bs.select('span')]
        d = dict(zip(h4s, spans))
        # e.g. 'کد معاملاتی نماد', 'IRO1MSMI0001'
        k, v = bs.select_one('span')['title'].split(' :')
        d[k] = v
        return d

    def statistic(self, days: _Literal[365, 180, 90, 30, 7]) -> _DataFrame:
        return _read_html(
            _fipiran(f'Symbol/statistic{days}?inscode={self.inscode}'))[0]

    def company_info(self):
        text = _fipiran(
            f'Symbol/CompanyInfoIndex?symbolpara={self._symbolpara}')
        bs = _soup(text)
        keys = [i.text.strip(': ') for i in bs.select('.media-body > h4')]
        values = [i.text.strip() for i in bs.select('.media-body span')]
        return dict(zip(keys, values))

    def price_history(self, rows: int = 365, page : int = 1) -> dict:
        j = _fipiran(
            'Symbol/HistoryPricePaging?'
            f'symbolpara={self._symbolpara}&rows={rows}&page={page}',
            json_resp=True)
        df = j['data'] = _DataFrame(j['data'], copy=False)
        df['gDate'] = _to_datetime(df['gDate'])
        df.set_index('gDate', inplace=True)
        return j


def search(term) -> list[Symbol]:
    """Note: the returned symbol objects will have `l30` attribute."""
    symbols = []
    append = symbols.append
    for result in _fipiran('Home/AutoComplete', (('term', term),), True):
        symbol = Symbol(result['LVal18AFC'])
        symbol.l30 = result['LSoc30']
        append(symbol)
    return symbols


_soup = _partial(_BeautifulSoup, features='lxml')
