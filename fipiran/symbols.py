from __future__ import annotations as _

from datetime import datetime as _datetime
from enum import Flag as _Flag, auto as _auto
from typing import Literal as _Literal

from pandas import DataFrame as _Df
from pydantic import RootModel as _RootModel

from fipiran import _api, _LoosModel as _LooseModel


class _InstrumentInfo(_LooseModel):
    status: int
    message: str
    item: list[InstrumentInfo]


class InstrumentInfo(_LooseModel):
    instrument: Instrument
    instrumentTransaction: InstrumentTransaction
    instrument5BestLimits: list[Instrument5BestLimit]
    instrumentClientTypes: list[InstrumentClientType]


class Instrument(_LooseModel):
    insCode: str
    smallSymbolName: str
    symbolFullName: str
    industryGroupCode: str
    industryGroupName: str | None
    industrySubCode: str
    industrySubName: str | None
    symbolStatus: str
    type: int
    marketCode: int
    staticThresholdMaxPrice: None
    staticThresholdMinPrice: None
    status: int


class InstrumentTransaction(_LooseModel):
    insCode: str
    transactionDate: _datetime
    numberOfTransactions: float
    numberOfVolume: float
    transactionValue: float
    closingPrice: float
    adjPriceForward: None | float
    adjPriceBackward: None | float
    lastTransaction: float
    changePrice: float
    priceMin: float
    priceMax: float
    priceFirst: float
    priceYesterday: float
    priceYesterdayBackward: float
    lastStatus: int
    hEven: int


class Instrument5BestLimit(_LooseModel):
    rowNumber: int
    demandVolume: int
    numberRequests: int
    demandPrice: int
    supplyPrice: int
    numberSupply: int
    supplyVolume: int


class InstrumentClientType(_LooseModel):
    numberIndividualsBuyers: int
    numberNonIndividualBuyers: int
    sumIndividualBuyVolume: int
    sumNonIndividualBuyVolume: int
    numberIndividualsSellers: int
    numberNonIndividualSellers: int
    sumIndividualSellVolume: int
    sumNonIndividualSellVolume: int


class Statistics(_LooseModel):
    weekly: PeriodStatistics
    monthly: PeriodStatistics
    quarterly: PeriodStatistics
    sixMonth: PeriodStatistics
    annual: PeriodStatistics


class PeriodStatistics(_LooseModel):
    priceMax: float
    priceMin: float
    numberOfTransactions: float
    numberOfVolume: float
    transactionValue: float


class Publisher(_LooseModel):
    name: str
    activitySubject: str
    executiveManager: str
    auditorName: str
    financialManager: str
    website: None | str
    address: None | str
    shareOfficeAddress: str
    telNo: None | str
    faxNo: None | str
    email: None | str
    listedCapital: int
    financialYear: str
    nationalCode: str
    isinCode: str


class Efficiency(_LooseModel):
    weeklyEfficiency: float
    monthlyEfficiency: float
    quarterlyEfficiency: float
    sixMonthEfficiency: float
    annualEfficiency: float


class _History(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[HistoryItem]


class HistoryItem(_LooseModel):
    insCode: str
    transactionDate: _datetime
    numberOfTransactions: float | None
    numberOfVolume: float | None
    transactionValue: float | None
    closingPrice: float | None
    adjPriceForward: float | None
    adjPriceBackward: float | None
    lastTransaction: float | None
    changePrice: float | None
    priceMin: float | None
    priceMax: float | None
    priceFirst: float | None
    priceYesterday: float | None
    lastStatus: int | None
    hEven: int | None


class _Statements(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[Statement]


class Statement(_LooseModel):
    title: str
    publishDateTime: _datetime
    letterType: int
    letterName: str
    letterKind: int
    isAudited: bool
    period: int
    auditorId: int
    auditorName: str
    yearEndToDate: _datetime | None
    htmlUrl: str
    pdfUrl: str
    excelUrl: str
    attachmentUrl: str
    attachments: list[Attachment]


class Attachment(_LooseModel):
    title: str
    attachmentDateTime: _datetime
    url: str


class Symbol:
    __slots__ = 'ins_code'

    def __init__(self, ins_code: str):
        self.ins_code = ins_code

    def __repr__(self):
        return f'{type(self).__name__}({self.ins_code!r})'

    def __eq__(self, other):
        return isinstance(other, Symbol) and other.ins_code == self.ins_code

    async def info(self) -> InstrumentInfo:
        return (
            await _api(
                'instrument/getinstrument',
                model=_InstrumentInfo,
                params={'insCode': self.ins_code},
            )
        ).item[0]

    async def statistics(self, date: _datetime) -> Statistics:
        return await _api(
            'instrument/instrumentperiodicstatistics',
            params={'insCode': self.ins_code, 'date': date.isoformat()},
            model=Statistics,
        )

    async def efficiency(self, date: _datetime) -> Efficiency:
        return await _api(
            'instrument/getefficiency',
            params={'insCode': self.ins_code, 'date': date.isoformat()},
            model=Efficiency,
        )

    async def publisher(self) -> Publisher:
        return await _api(
            'codal/publisher',
            params={'insCode': self.ins_code},
            model=Publisher,
        )

    async def history(self, *, limit: int = 99999) -> _Df:
        items = (
            await _api(
                'instrument/instrumenthistory',
                params={
                    'insCode': self.ins_code,
                    'pageSize': limit,
                    'pageIndex': 0,
                },
                model=_History,
            )
        ).items
        return _Df(vars(i) for i in items)

    async def statements(self, limit: int = 100) -> list[Statement]:
        return (
            await _api(
                'codal/statements',
                params={
                    'insCode': self.ins_code,
                    'pageSize': limit,
                    'pageIndex': 0,
                },
                model=_Statements,
            )
        ).items

    @staticmethod
    async def from_name(name: str, /):
        instruments, _ = await search(symbol=name, limit=1)
        return Symbol(instruments[0].insCode)


class CSVFlag(_Flag):
    api_map: dict

    def __str__(self) -> str:
        """Return a CSV representation of the chosen flags."""
        cls = type(self)
        if cls.ALL in self:  # type: ignore
            return ''
        # breakpoint()
        return ','.join([cls.api_map[flag.name] for flag in self])


class MarketType(CSVFlag):
    TEHRAN_STOCK_EXCHANGE = _auto()  # 1
    IRAN_FARA_BOURSE = _auto()  # 2
    FARA_BOURSE_OTC = _auto()  # 4
    FUTURES = _auto()  # 8
    ENERGY_EXCHANGE = _auto()  # 16
    COMMODITY_EXCHANGE = _auto()  # 32


MarketType.api_map = {
    MarketType.TEHRAN_STOCK_EXCHANGE: '1',
    MarketType.IRAN_FARA_BOURSE: '2',
    MarketType.FARA_BOURSE_OTC: '4',
    MarketType.FUTURES: '3',
    MarketType.ENERGY_EXCHANGE: '6',
    MarketType.COMMODITY_EXCHANGE: '7',
}


class SymbolType(CSVFlag):
    # --- A. Equity/Ordinary Shares (سهام عادی) ---
    ORDINARY_SHARES_TSE = _auto()  # Maps to '300'
    ORDINARY_SHARES_IFB = _auto()  # Maps to '303'
    ORDINARY_SHARES_IFB_OTC = _auto()  # Maps to '309'
    ORDINARY_SHARES_IFB_FACILITIES = _auto()  # Maps to '307'
    ORDINARY_SHARES_IFB_SME = _auto()  # Maps to '313'

    # --- B. Right of Preference (حق تقدم) ---
    RIGHTS_TSE = _auto()  # Maps to '400'
    RIGHTS_IFB = _auto()  # Maps to '403'
    RIGHTS_IFB_OTC = _auto()  # Maps to '404'
    RIGHTS_IFB_SME = _auto()  # Maps to '401'

    # --- C. Participation/Debt Securities (اوراق مشارکت) ---
    PARTICIPATION_BOND_QUOTATION = _auto()  # Maps to '402'
    PARTICIPATION_BOND_SUKUK = _auto()  # Maps to '208'
    PARTICIPATION_BOND_PRIVATE_SUKUK = _auto()  # Maps to '706'
    PARTICIPATION_BOND_IFB = _auto()  # Maps to '306'

    # --- D. Funds and Others ---
    ETF_FUNDS_TSE = _auto()  # Maps to '305'
    INTELLECTUAL_PROPERTY = _auto()  # Maps to '903'


SymbolType.api_map = {
    SymbolType.ORDINARY_SHARES_TSE: '300',
    SymbolType.ORDINARY_SHARES_IFB: '303',
    SymbolType.ORDINARY_SHARES_IFB_OTC: '309',
    SymbolType.ORDINARY_SHARES_IFB_FACILITIES: '307',
    SymbolType.ORDINARY_SHARES_IFB_SME: '313',
    SymbolType.RIGHTS_TSE: '400',
    SymbolType.RIGHTS_IFB: '403',
    SymbolType.RIGHTS_IFB_OTC: '404',
    SymbolType.RIGHTS_IFB_SME: '401',
    SymbolType.PARTICIPATION_BOND_QUOTATION: '402',
    SymbolType.PARTICIPATION_BOND_SUKUK: '208',
    SymbolType.PARTICIPATION_BOND_PRIVATE_SUKUK: '706',
    SymbolType.PARTICIPATION_BOND_IFB: '306',
    SymbolType.ETF_FUNDS_TSE: '305',
    SymbolType.INTELLECTUAL_PROPERTY: '903',
}


class SymbolStatus(CSVFlag):
    PROHIBITED = _auto()  # Maps to 'I' (ممنوع)
    ALLOWED = _auto()  # Maps to 'A' (مجاز)
    ALLOWED_BLOCKED = _auto()  # Maps to 'AG' (مجاز-مسدود)
    ALLOWED_STOPPED = _auto()  # Maps to 'AS' (مجاز-متوقف)
    ALLOWED_RESERVED = _auto()  # Maps to 'AR' (مجاز-محفوظ)
    PROHIBITED_BLOCKED = _auto()  # Maps to 'IG' (ممنوع-مسدود)
    PROHIBITED_STOPPED = _auto()  # Maps to 'IS' (ممنوع-متوقف)
    PROHIBITED_RESERVED = _auto()  # Maps to 'IR' (ممنوع-محفوظ)


SymbolStatus.api_map = {
    SymbolStatus.PROHIBITED: 'I',
    SymbolStatus.ALLOWED: 'A',
    SymbolStatus.ALLOWED_BLOCKED: 'AG',
    SymbolStatus.ALLOWED_STOPPED: 'AS',
    SymbolStatus.ALLOWED_RESERVED: 'AR',
    SymbolStatus.PROHIBITED_BLOCKED: 'IG',
    SymbolStatus.PROHIBITED_STOPPED: 'IS',
    SymbolStatus.PROHIBITED_RESERVED: 'IR',
}


class _Search(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[SearchResults]


class SearchResults(_LooseModel):
    instruments: list[Instrument]
    instrumentTransactions: list[InstrumentTransaction]


async def search(
    *,
    markettype: MarketType | None = None,
    symboltype: SymbolType | None = None,
    symbolstatus: SymbolStatus | None = None,
    symbol: str | None = None,
    company: str | None = None,
    idx_code: str | None = None,
    industry: str | None = None,
    sub_industry: str | None = None,
    limit: int = 999999,
    sort: _Literal['asc', 'desc'] = 'asc',
    column: _Literal[
        'smallSymbolName',
        'symbolFullName',
        'transactionDate',
        'numberOfTransactions',
        'numberOfVolume',
        'transactionValue',
        'priceYesterday',
        'priceFirst',
        'lastTransaction',
        'closingPrice',
        'priceMin',
        'priceMax',
    ] = 'smallSymbolName',
) -> tuple[list[Instrument], list[InstrumentTransaction]]:
    """https://www.fipiran.com/symbol/list.

    You can use the following functions for finding the appropriate
    code for the following parameters:
        industry: symbols.industries
        sub_industry: symbols.sub_industries
        idx_code: symbols.index_compare
    """
    params = {
        'pageIndex': 0,
        'pageSize': limit,
        'sort': sort,
        'column': column,
    }
    if symbol is not None:
        params['symbol'] = symbol
    if idx_code is not None:
        params['idx_code'] = idx_code
    if symboltype is not None:
        params['symboltype'] = symboltype
    if symbolstatus is not None:
        params['symbolstatus'] = symbolstatus
    if markettype is not None:
        params['markettype'] = markettype
    if company is not None:
        params['company'] = company
    if sub_industry is not None:
        params['subIndustry'] = sub_industry
    if industry is not None:
        params['industry'] = industry
    m = await _api(
        'instrument/instrumentcompare', params=params, model=_Search
    )
    r = m.items[0]
    return (r.instruments, r.instrumentTransactions)


class IndexData(_LooseModel):
    insCode: str
    title: str
    date: _datetime
    clock: int
    numberSymbolsTraded: int
    reducedNumberSymbols: int
    numberSymbolsIncreased: int
    numberSymbolsWithoutChange: int
    numberSymbolsNotTraded: int
    numberBookingSymbols: int
    numberSuspendedSymbols: int
    totalNumberSymbols: int
    timeMaximum: int
    timeMinimum: int
    lastValueDay: float
    maximumValueDayIndex: float
    minimumValueDayIndex: float
    cashReturnIndexValue: float
    percentageIndexChanges: float
    percentageIndexChangesDayByPreviousDay: float
    percentageAverageChangeSymbols: float
    averagePercentageChangeSymbolsReduced: float
    percentageMeanSymbolChangeIncreased: float
    dailyEfficiency: float
    weeklyEfficiency: float
    monthlyEfficiency: float
    quarterlyEfficiency: float
    sixMonthEfficiency: float
    annualEfficiency: float


class _IndexCompare(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[IndexData]


async def index_compare() -> list[IndexData]:
    m = await _api('index/indexcompare', model=_IndexCompare)
    items = m.items
    assert m.totalCount <= len(items)
    return items


class Industry(_LooseModel):
    industryGroupCode: str
    title: str


async def industries() -> list[Industry]:
    return (
        await _api('instrument/getindustry', model=_RootModel[list[Industry]])
    ).root


class SubIndustry(_LooseModel):
    industrySubCode: str
    title: str
    industryGroupCode: str
    date: _datetime


async def sub_industries() -> list[SubIndustry]:
    return (
        await _api(
            'instrument/getindustrysub', model=_RootModel[list[SubIndustry]]
        )
    ).root
