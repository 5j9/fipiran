from __future__ import annotations as _

from datetime import (
    datetime as _datetime,
    timedelta as _timedelta,
    timezone as _timezone,
)
from typing import Annotated as _Annotated

import polars as _pl
from pydantic import (
    AfterValidator as _AfterValidator,
    BaseModel as _BaseModel,
    RootModel as _RootModel,
)

from fipiran import _api, _LooseModel


class _SpecificFundInfo(_LooseModel):
    status: int
    message: str
    item: SpecificFundInfo


class _CommonFundInfo(_LooseModel):
    date: _datetime
    regNo: str
    name: str
    rankOf12Month: float | None = None
    rankOf24Month: float | None = None
    rankOf36Month: float | None = None
    rankOf48Month: float | None = None
    rankOf60Month: float | None = None
    initiationDate: _datetime
    fundType: int | None = None
    typeOfInvest: str
    dailyEfficiency: float | None = None
    weeklyEfficiency: float | None = None
    monthlyEfficiency: float | None = None
    quarterlyEfficiency: float | None = None
    sixMonthEfficiency: float | None = None
    annualEfficiency: float | None = None
    efficiency: float | None = None
    cancelNav: float | None = None
    issueNav: float | None = None
    statisticalNav: float | None = None
    dividendIntervalPeriod: int | None = None
    netAsset: int | None = None
    fundSize: int | None = None
    beta: float | None = None
    alpha: float | None = None


class FundRank(_LooseModel):
    id: int
    regNo: str
    reportFileContentType: str | None = None
    calculationDetailsUrl: str
    reportUrl: str
    lastUpdate: _datetime
    reportFileName: str | None = None
    reportFile: str | None = None
    rankOfSeason: float
    rankOf36Month: float | None = None
    rankOf24Month: float | None = None
    rankOf12Month: float | None = None


class SpecificFundInfo(_CommonFundInfo):
    articlesOfAssociationLink: None = None
    auditor: str
    baseTotalUnit: None = None
    baseUnitsCancelNAV: None = None
    baseUnitsSubscriptionNAV: None = None
    baseUnitsTotalCancel: None = None
    baseUnitsTotalNetAssetValue: None = None
    baseUnitsTotalSubscription: None = None
    bond: float
    cash: float
    commodity: float | None = None
    custodian: str
    deposit: float
    estimatedEarningRate: None = None
    executiveManager: str | None = None
    fiveBest: float
    fundPublisher: int
    fundRank: FundRank | None = None
    fundUnit: float | None = None
    fundWatch: None = None
    groupId: int
    groupName: str | None = None
    guaranteedEarningRate: int | None = None
    guarantor: str
    guarantorSeoRegisterNo: None = None
    insCode: str | None = None
    insInvNo: int
    insInvPercent: float | None = None
    investedUnits: int
    investmentManager: str
    isCompleted: bool
    lastModificationTime: _datetime
    legalPercent: float
    manager: str
    managerSeoRegisterNo: str
    marketMaker: str | None = None
    mutualFundLicenses: list[MutualFundLicense]
    nationalId: str
    naturalPercent: float
    other: float
    prosoectusLink: None = None
    registerDate: _datetime
    registrationNumber: str
    retInvNo: int
    retInvPercent: float | None = None
    seoRegisterDate: _datetime
    smallSymbolName: str | None = None
    stock: float
    superTotalUnit: None = None
    superUnitsCancelNAV: None = None
    superUnitsSubscriptionNAV: None = None
    superUnitsTotalCancel: None = None
    superUnitsTotalNetAssetValue: None = None
    superUnitsTotalSubscription: None = None
    unitsRedDAY: int
    unitsRedFromFirst: int
    unitsSubDAY: int
    unitsSubFromFirst: int
    websiteAddress: list[str]


class MutualFundLicense(_LooseModel):
    id: int
    regNo: str
    expireDate: None = None
    isExpired: bool
    startDate: _datetime
    licenseNo: str
    licenseStatusId: int
    licenseStatusDescription: None = None
    licenseTypeId: int
    newLicenseTypeId: None = None
    mutualFund: None = None


class AlphaBeta(_LooseModel):
    date: _datetime
    beta: float
    alpha: float


class AssetsOnDate(_LooseModel):
    date: _datetime
    netAsset: int
    unitsSubDAY: int
    unitsRedDAY: int


class NavOnDate(_LooseModel):
    date: _datetime
    issueNav: float
    cancelNav: float
    statisticalNav: float


class PortfolioOnDate(_LooseModel):
    date: _datetime
    fiveBest: float
    stock: float
    bond: float
    other: float
    cash: float
    deposit: float


class Fund:
    __slots__ = ('group_id', 'reg_no')

    def __init__(self, reg_no: int | str, group_id: str | int = '0'):
        self.reg_no = reg_no
        self.group_id = group_id

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r}, {self.group_id!r})'

    async def _api[T: _BaseModel](
        self, path, *, model: type[T], **kwargs
    ) -> T:
        params = {'regno': self.reg_no, 'groupId': self.group_id}
        kw_params = kwargs.get('params')
        if kw_params is not None:
            params |= kw_params
        return await _api(
            path=path,
            params=params,
            model=model,
        )

    async def asset_allocation_history(self) -> _pl.LazyFrame:
        """Return a LazyFrame of asset type percentages.

        See funds.PortfolioOnDate for column names.
        """
        m = await self._api(
            'chart/portfoliochart',
            model=_RootModel[list[PortfolioOnDate]],
        )
        return _pl.LazyFrame(
            [vars(i) for i in m.root], infer_schema_length=None
        )

    async def navps_history(self, /, *, all_=True) -> _pl.LazyFrame:
        """Return NAVPS history as a LazyFrame sorted by date.

        See funds.NavOnDate for column names.
        """
        m = await self._api(
            'chart/getfundchart',
            params={'showAll': str(all_).lower()},
            model=_RootModel[list[NavOnDate]],
        )
        return _pl.LazyFrame(
            [vars(i) for i in m.root], infer_schema_length=None
        ).sort('date')

    async def nav_history(self, /, *, all_=True) -> _pl.LazyFrame:
        """Return NAV history as a LazyFrame sorted by date.

        See funds.AssetsOnDate for column names.
        """
        m = await self._api(
            'chart/getfundnetassetchart',
            params={'showAll': str(all_).lower()},
            model=_RootModel[list[AssetsOnDate]],
        )
        return _pl.LazyFrame(vars(i) for i in m.root).sort('date')

    async def alpha_beta(self, /, *, all_=True) -> _pl.LazyFrame:
        """Return alpha/beta history as a LazyFrame sorted by date."""
        items = (
            await self._api(
                'chart/alphabetachart',
                params={'showAll': str(all_).lower()},
                model=_RootModel[list[AlphaBeta]],
            )
        ).root
        return _pl.LazyFrame(vars(i) for i in items).sort('date')

    async def info(self) -> SpecificFundInfo:
        return (await self._api('fund/getfund', model=_SpecificFundInfo)).item


def _fix_website_address(lf: _pl.LazyFrame) -> _pl.LazyFrame:
    return lf.with_columns(
        _pl.col('websiteAddress').list.get(0, null_on_oob=True)
    )


class _Funds(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[FundInfo]


_TEHRAN = _timezone(_timedelta(hours=3, minutes=30))


def _ensure_tehran(value: _datetime) -> _datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=_TEHRAN)
    return value.astimezone(_TEHRAN)


_TehranDatetime = _Annotated[
    _datetime,
    _AfterValidator(_ensure_tehran),
]


class FundInfo(_CommonFundInfo):
    articlesOfAssociationLink: None = None
    auditor: str
    bond: float | None = None
    cash: float | None = None
    commodity: float | None = None
    custodian: str
    deposit: float | None = None
    estimatedEarningRate: float | None = None
    fiveBest: float | None = None
    fundPublisher: int
    fundUnit: float | None = None
    fundWatch: None = None
    groupId: int
    guaranteedEarningRate: int | None = None
    guarantor: str
    guarantorSeoRegisterNo: str | None = None
    insCode: str | None = None
    investedUnits: int | None = None
    isCompleted: bool
    manager: str
    managerSeoRegisterNo: str | None = None
    other: float | None = None
    prosoectusLink: None = None
    rankLastUpdate: _TehranDatetime
    rankOfSeason: float
    smallSymbolName: str | None = None
    stock: float | None = None
    websiteAddress: list[str]


async def funds() -> _pl.LazyFrame:
    """Return a LazyFrame representing https://www.fipiran.com/mf/list.

    See funds.FundInfo for column names.
    """
    m = await _api(
        'fund/fundcompare/',
        model=_Funds,
        method='post',
        json={
            'regNos': [],
            'showMarketMakers': False,
        },
    )
    assert m.totalCount <= m.pageSize
    lf = _pl.LazyFrame([vars(i) for i in m.items], infer_schema_length=None)
    return _fix_website_address(lf)


class _FundTypes(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[FundType]


class FundType(_LooseModel):
    fundType: int
    name: str
    isActive: bool


async def fund_types() -> _pl.LazyFrame:
    """See funds.FundType for column names."""
    m = await _api('fund/fundtype', model=_FundTypes)
    assert m.totalCount <= m.pageSize
    return _pl.LazyFrame([vars(i) for i in m.items])


class AverageReturns(_LooseModel):
    id: int
    fundTypeId: int | None
    netAsset: int | None = None
    stock: float | None = None
    bond: float | None = None
    cash: float | None = None
    deposit: float | None = None
    dailyEfficiency: float | None = None
    weeklyEfficiency: float | None = None
    monthlyEfficiency: float | None = None
    quarterlyEfficiency: float | None = None
    sixMonthEfficiency: float | None = None
    annualEfficiency: float | None = None
    efficiency: float | None = None


async def average_returns() -> _pl.LazyFrame:
    """Return a LazyFrame for https://www.fipiran.com/mf/efficiency.

    See AverageReturns for column names.
    """
    m = await _api(
        'fund/averagereturns', model=_RootModel[list[AverageReturns]]
    )
    return _pl.LazyFrame(vars(i) for i in m.root).with_columns(
        _pl.col('netAsset').cast(_pl.Int64)
    )


class _TreeMap(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[TreeMapItem]


class TreeMapItem(_CommonFundInfo):
    articlesOfAssociationLink: None = None
    auditor: str
    bond: float | None = None
    cash: float | None = None
    commodity: float | None = None
    custodian: str
    deposit: float | None = None
    estimatedEarningRate: float | None = None
    fiveBest: float | None = None
    fundPublisher: int
    fundUnit: float | None = None
    fundWatch: None = None
    groupId: int
    guaranteedEarningRate: int | None = None
    guarantor: str
    guarantorSeoRegisterNo: str | None = None
    insCode: str | None = None
    investedUnits: int | None = None
    isCompleted: bool
    manager: str
    managerSeoRegisterNo: str | None = None
    other: float | None = None
    prosoectusLink: None = None
    rankLastUpdate: _datetime
    stock: float | None = None
    websiteAddress: list[str]


async def map_data() -> _pl.LazyFrame:
    """See TreeMapItem for column names."""
    m = await _api('fund/treemap', model=_TreeMap)
    lf = _pl.LazyFrame([vars(i) for i in m.items], infer_schema_length=None)
    return _fix_website_address(lf)


class _DepData(_LooseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[DepItem]


class DepItem(_CommonFundInfo):
    rankLastUpdate: _datetime
    tempGuarantorName: str | None = None
    tempManagerName: str | None
    manager: Manager | None
    guarantor: Guarantor | None = None


class Manager(_LooseModel):
    address: str | None = None
    ceo: str | None = None
    cfiId: int | None = None
    cfiLastModificationTime: _datetime | None = None
    email: str | None = None
    isCompleted: bool
    managerId: int
    managerNationalCode: str | None = None
    managerSeoRegisterNo: str | None = None
    name: str
    nationalId: str | None = None
    registerDate: _datetime | None = None
    registeredCapital: int | None = None
    registerPlace: None = None
    registerPlaceId: None = None
    registrationNumber: str | None = None
    seoRegisterDate: _datetime | None = None
    tel: str | None = None
    type: int | None = None
    webSite: str | None = None


class Guarantor(_LooseModel):
    address: str | None = None
    ceo: str | None = None
    cfiId: int | None = None
    cfiLastModificationTime: _datetime | None = None
    email: str | None = None
    guarantorId: int
    guarantorNationalCode: str | None = None
    guarantorSeoRegisterNo: str
    isCompleted: bool
    name: str
    nationalId: str | None = None
    registerDate: _datetime | None = None
    registeredCapital: int | None = None
    registerPlace: None = None
    registerPlaceId: None = None
    registrationNumber: str | None = None
    seoRegisterDate: _datetime | None = None
    tel: str | None = None
    type: int | None = None
    webSite: str | None = None


async def dependency_graph_data() -> _pl.LazyFrame:
    """See DepItem for column names."""
    m = await _api('fund/dependencygraph', model=_DepData)
    return _pl.LazyFrame(vars(i) for i in m.items)
