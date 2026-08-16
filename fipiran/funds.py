from __future__ import annotations as _

from datetime import datetime as _datetime

import polars as _pl
from pydantic import BaseModel as _BaseModel, RootModel as _RootModel

from fipiran import _api, _LooseModel


class _SpecificFundInfo(_LooseModel):
    status: int
    message: str
    item: SpecificFundInfo


class _CommonFundInfo(_LooseModel):
    date: _datetime
    regNo: str
    name: str
    rankOf12Month: float | None
    rankOf24Month: float | None
    rankOf36Month: float | None
    rankOf48Month: float | None
    rankOf60Month: float | None
    initiationDate: _datetime
    fundType: int | None
    typeOfInvest: str
    dailyEfficiency: float | None
    weeklyEfficiency: float | None
    monthlyEfficiency: float | None
    quarterlyEfficiency: float | None
    sixMonthEfficiency: float | None
    annualEfficiency: float | None
    efficiency: float | None
    cancelNav: float | None
    issueNav: float | None
    statisticalNav: float | None
    dividendIntervalPeriod: int | None
    netAsset: int | None
    fundSize: int | None
    beta: float | None
    alpha: float | None


class SpecificFundInfo(_CommonFundInfo):
    smallSymbolName: str | None = None
    guaranteedEarningRate: int | None
    # executiveManager: str
    articlesOfAssociationLink: None
    prosoectusLink: None
    lastModificationTime: _datetime
    estimatedEarningRate: None
    insInvNo: int
    # insInvPercent: float
    legalPercent: float
    # marketMaker: str
    naturalPercent: float
    retInvNo: int
    # retInvPercent: float
    investedUnits: int
    unitsRedDAY: int
    unitsRedFromFirst: int
    unitsSubDAY: int
    unitsSubFromFirst: int
    fiveBest: float
    stock: float
    bond: float
    other: float
    cash: float
    deposit: float
    fundUnit: float | None
    commodity: float | None
    manager: str
    managerSeoRegisterNo: str
    guarantorSeoRegisterNo: None
    auditor: str
    websiteAddress: list[str]
    custodian: str
    guarantor: str
    investmentManager: str
    fundWatch: None
    seoRegisterDate: _datetime
    registrationNumber: str
    registerDate: _datetime
    nationalId: str
    isCompleted: bool
    # insCode: str
    baseUnitsSubscriptionNAV: None
    baseUnitsCancelNAV: None
    baseUnitsTotalNetAssetValue: None
    baseTotalUnit: None
    baseUnitsTotalSubscription: None
    baseUnitsTotalCancel: None
    superUnitsSubscriptionNAV: None
    superUnitsCancelNAV: None
    superUnitsTotalNetAssetValue: None
    superTotalUnit: None
    superUnitsTotalSubscription: None
    superUnitsTotalCancel: None
    fundPublisher: int
    mutualFundLicenses: list[MutualFundLicense]


class MutualFundLicense(_LooseModel):
    id: int
    regNo: str
    isExpired: bool
    startDate: _datetime
    expireDate: None
    licenseNo: str
    licenseStatusId: int
    licenseStatusDescription: None
    licenseTypeId: int
    newLicenseTypeId: None
    mutualFund: None


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


class FundInfo(_CommonFundInfo):
    smallSymbolName: str | None
    guaranteedEarningRate: int | None
    estimatedEarningRate: float | None
    investedUnits: int | None
    articlesOfAssociationLink: None
    prosoectusLink: None
    websiteAddress: list[str]
    manager: str
    managerSeoRegisterNo: str | None
    guarantorSeoRegisterNo: str | None
    auditor: str
    custodian: str
    guarantor: str
    isCompleted: bool
    fiveBest: float | None
    stock: float | None
    bond: float | None
    other: float | None
    cash: float | None
    deposit: float | None
    fundUnit: float | None
    commodity: float | None
    fundPublisher: int
    insCode: str | None = None
    fundWatch: None


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
    netAsset: int | None
    stock: float | None
    bond: float | None
    cash: float | None
    deposit: float | None
    dailyEfficiency: float | None
    weeklyEfficiency: float | None
    monthlyEfficiency: float | None
    quarterlyEfficiency: float | None
    sixMonthEfficiency: float | None
    annualEfficiency: float | None
    efficiency: float | None


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
    guaranteedEarningRate: int | None
    estimatedEarningRate: float | None
    investedUnits: int
    articlesOfAssociationLink: None
    prosoectusLink: None
    websiteAddress: list[str]
    manager: str
    managerSeoRegisterNo: str | None
    guarantorSeoRegisterNo: str | None
    auditor: str
    custodian: str
    guarantor: str
    isCompleted: bool
    fiveBest: float
    stock: float | None
    bond: float | None
    other: float
    cash: float
    deposit: float
    fundUnit: float | None
    commodity: float | None
    fundPublisher: int
    insCode: str | None = None
    fundWatch: None


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
    tempGuarantorName: str | None
    tempManagerName: str | None
    manager: Manager | None
    guarantor: Guarantor | None


class Manager(_LooseModel):
    managerId: int
    cfiId: int | None
    managerSeoRegisterNo: str | None
    name: str
    managerNationalCode: str | None
    type: int | None
    seoRegisterDate: _datetime | None
    registeredCapital: int | None
    webSite: str | None
    email: str | None
    ceo: str | None
    tel: str | None
    address: str | None
    nationalId: str | None
    registrationNumber: str | None
    registerPlace: None
    registerPlaceId: None
    registerDate: _datetime | None
    cfiLastModificationTime: _datetime | None
    isCompleted: bool


class Guarantor(_LooseModel):
    guarantorId: int
    cfiId: int | None
    guarantorSeoRegisterNo: str
    name: str
    guarantorNationalCode: str | None
    type: int | None
    seoRegisterDate: _datetime | None
    registeredCapital: int | None
    webSite: str | None
    email: str | None
    ceo: str | None
    tel: str | None
    address: str | None
    nationalId: str | None
    registrationNumber: str | None
    registerPlace: None
    registerPlaceId: None
    registerDate: _datetime | None
    cfiLastModificationTime: _datetime | None
    isCompleted: bool


async def dependency_graph_data() -> _pl.LazyFrame:
    """See DepItem for column names."""
    m = await _api('fund/dependencygraph', model=_DepData)
    return _pl.LazyFrame(vars(i) for i in m.items)
