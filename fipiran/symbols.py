from io import StringIO as _StringIO
from typing import Literal as _Literal

from jdatetime import datetime as _jdt
from lxml.html import HtmlElement as _HtmlElement, fromstring as _parse_html
from pandas import DataFrame as _Df, read_html as _rh, to_datetime as _tdt

from . import _fipiran

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
    async def inscode(self):
        if (inscode := getattr(self, '_inscode', None)) is not None:
            return inscode
        text = await _fipiran(f'Symbol?symbolpara={self._symbolpara}')
        start = text.find("'inscode': '") + 12
        end = text.find("'", start)
        self._inscode = inscode = int(text[start:end])
        return inscode

    async def price_data(self) -> dict:
        # note: some fields like Trailing P/E and Forward P/E are *currently*
        # not computed by fipiran and are always empty.
        text = await _fipiran(
            f'Symbol/_priceData?inscode={await self.inscode}'
        )
        tree: _HtmlElement = _parse_html(text)
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
            'PriceMin',
            'PriceMax',
            'PDrCotVal',
            'PriceFirst',
            'PClosing',
            'changepdr',
            'changepc',
            'prevPrice',
            'ZTotTran',
            'QTotTran5J',
            'QTotCap',
        ):
            d[k] = num(tree.xpath(f"//*[@id='{k}']/text()")[0])

        d['Deven'] = _jdt.strptime(
            tree.xpath("//td[@id='Deven']/text()")[0], '%Y/%m/%d-%H:%M:%S'
        )

        tmin, tmax = (
            tree.xpath(
                "//td[text()='قیمت مجاز']/following-sibling::td[1]/text()"
            )[0]
            .strip()
            .split(' - ')
        )
        d['tmin'] = num(tmin)
        d['tmax'] = num(tmax)

        return d

    async def best_limit_data(self) -> list[_Df]:
        text = await _fipiran(
            f'Symbol/_BestLimitData?inscode={await self.inscode}'
        )
        return _rh(_StringIO(text))

    async def reference_data(self) -> dict:
        text = await _fipiran(
            f'Symbol/_RefrenceData?symbolpara={self._symbolpara}'
        )
        tree = _parse_html(text)
        h4s = [i.strip(': ') for i in tree.xpath('.//h4/text()')]
        spans = tree.xpath('.//span')
        d = dict(zip(h4s, [i.text for i in spans]))
        # Add ISIN e.g. 'کد معاملاتی نماد', 'IRO1MSMI0001'
        k, v = spans[0].get('title').split(' :')
        d[k] = v
        return d

    async def statistic(self, days: _Literal[365, 180, 90, 30, 7]) -> _Df:
        return _rh(
            _StringIO(
                await _fipiran(
                    f'Symbol/statistic{days}?inscode={await self.inscode}'
                )
            )
        )[0]

    async def company_info(self):
        text = await _fipiran(
            f'Symbol/CompanyInfoIndex?symbolpara={self._symbolpara}'
        )
        tree = _parse_html(text)
        d = {}
        for body in tree.xpath("//*[contains(@class, 'media-body')]"):
            key = body.xpath('normalize-space(h4)').strip(': ')
            value = body.xpath('normalize-space(.//span)')
            d[key] = value
        return d

    async def price_history(self, rows: int = 365, page: int = 1) -> dict:
        j = await _fipiran(
            'Symbol/HistoryPricePaging?'
            f'symbolpara={self._symbolpara}&rows={rows}&page={page}',
            json_resp=True,
        )
        df = j['data'] = _Df(j['data'], copy=False)
        df['gDate'] = _tdt(df['gDate'])
        df.set_index('gDate', inplace=True)
        return j


async def search(term) -> list[Symbol]:
    """Note: the returned symbol objects will have `l30` attribute."""
    symbols = []
    append = symbols.append
    for result in await _fipiran('Home/AutoComplete', (('term', term),), True):
        symbol = Symbol(result['LVal18AFC'])
        symbol.l30 = result['LSoc30']
        append(symbol)
    return symbols
