from __future__ import annotations as _

from datetime import datetime as _datetime

from pandas import NA as _NA, DataFrame as _Df
from pydantic import BaseModel as _BaseModel, RootModel as _RootModel

from fipiran import _api


class _SpecificFundInfo(_BaseModel):
    status: int
    message: str
    item: SpecificFundInfo


class _CommonFundInfo(_BaseModel):
    regNo: str
    name: str
    rankOf12Month: None | int
    rankOf24Month: None | int
    rankOf36Month: None | int
    rankOf48Month: None | int
    rankOf60Month: None | int
    initiationDate: _datetime


class SpecificFundInfo(_CommonFundInfo):
    fundSize: int
    fundType: int
    executiveManager: str
    articlesOfAssociationLink: None
    prosoectusLink: None
    lastModificationTime: _datetime
    date: _datetime
    dailyEfficiency: float
    weeklyEfficiency: float
    monthlyEfficiency: float
    quarterlyEfficiency: float
    sixMonthEfficiency: float
    annualEfficiency: float
    dividendIntervalPeriod: int
    estimatedEarningRate: None
    guaranteedEarningRate: None
    insInvNo: int
    insInvPercent: float
    legalPercent: float
    marketMaker: str
    naturalPercent: float
    netAsset: int
    retInvNo: int
    retInvPercent: float
    investedUnits: int
    unitsRedDAY: int
    unitsRedFromFirst: int
    unitsSubDAY: int
    unitsSubFromFirst: int
    efficiency: float
    cancelNav: float
    issueNav: float
    statisticalNav: float
    fiveBest: float
    stock: float
    bond: float
    other: float
    cash: float
    deposit: float
    fundUnit: float | None
    commodity: float | None
    typeOfInvest: str
    rankLastUpdate: _datetime
    manager: str
    managerSeoRegisterNo: str
    guarantorSeoRegisterNo: None
    auditor: str
    websiteAddress: list[str]
    custodian: str
    guarantor: str
    investmentManager: str
    beta: float
    alpha: float
    fundWatch: None
    seoRegisterDate: _datetime
    registrationNumber: str
    registerDate: _datetime
    nationalId: str
    isCompleted: bool
    insCode: str
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


class MutualFundLicense(_BaseModel):
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


class AlphaBeta(_BaseModel):
    date: _datetime
    beta: float
    alpha: float


class AssetsOnDate(_BaseModel):
    date: _datetime
    netAsset: int
    unitsSubDAY: int
    unitsRedDAY: int


class NavOnDate(_BaseModel):
    date: _datetime
    issueNav: float
    cancelNav: float
    statisticalNav: float


class PortfolioOnDate(_BaseModel):
    date: _datetime
    fiveBest: float
    stock: float
    bond: float
    other: float
    cash: float
    deposit: float
    fundUnit: float | None
    commodity: float | None


class Fund:
    __slots__ = 'reg_no'

    def __init__(self, reg_no: int | str):
        self.reg_no = reg_no

    def __repr__(self):
        return f'{type(self).__name__}({self.reg_no!r})'

    async def asset_allocation_history(self) -> _Df:
        """Return a dict where values are percentage of each kind of asset.

        See funds.PortfolioOnDate for column names.
        """
        m = await _api(
            f'chart/portfoliochart?regno={self.reg_no}',
            model=_RootModel[list[PortfolioOnDate]],
        )
        df = _Df(vars(i) for i in m.root)
        return df

    async def navps_history(self, /, *, all_=True) -> _Df:
        """Return NAVPS history as DataFrame.

        See funds.NavOnDate for column names.
        """
        m = await _api(
            f'chart/getfundchart?regno={self.reg_no}&showAll={str(all_).lower()}',
            model=_RootModel[list[NavOnDate]],
        )
        df = _Df(vars(i) for i in m.root)
        df.set_index('date', inplace=True)
        return df

    async def nav_history(self, /, *, all_=True) -> _Df:
        """Return NAV history as a DataFrame.

        See funds.AssetsOnDate for column names.
        """
        m = await _api(
            f'chart/getfundnetassetchart?regno={self.reg_no}&showAll={str(all_).lower()}',
            model=_RootModel[list[AssetsOnDate]],
        )
        df = _Df(vars(i) for i in m.root)
        df.set_index('date', inplace=True)
        return df

    async def alpha_beta(self, /, *, all_=True) -> _Df:
        """See funds.AlphaBeta for column names."""
        items = (
            await _api(
                f'chart/alphabetachart?regno={self.reg_no}&showAll={str(all_).lower()}',
                model=_RootModel[list[AlphaBeta]],
            )
        ).root
        df = _Df(vars(i) for i in items)
        df.set_index('date', inplace=True)
        return df

    async def info(self) -> SpecificFundInfo:
        return (
            await _api(
                f'fund/getfund?regno={self.reg_no}', model=_SpecificFundInfo
            )
        ).item


def _fix_website_address(df: _Df):
    # assert df['websiteAddress'].map(len).max() == 1
    df['websiteAddress'] = df['websiteAddress'].map(
        lambda lst: lst[0] if lst else _NA
    )


class _Funds(_BaseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[FundInfo]


class FundInfo(_CommonFundInfo):
    rankLastUpdate: _datetime
    fundType: int
    typeOfInvest: str
    fundSize: int | None
    dailyEfficiency: float | None
    weeklyEfficiency: float | None
    monthlyEfficiency: float | None
    quarterlyEfficiency: float | None
    sixMonthEfficiency: float | None
    annualEfficiency: float | None
    statisticalNav: float | None
    efficiency: float | None
    cancelNav: float | None
    issueNav: float | None
    dividendIntervalPeriod: int | None
    guaranteedEarningRate: None | int
    date: _datetime
    netAsset: int | None
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
    beta: float | None
    alpha: float | None
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
    smallSymbolName: str | None = None
    insCode: str | None = None
    fundWatch: None


async def funds() -> _Df:
    """Return the data available at https://www.fipiran.com/mf/list.

    See funds.FundInfo for column names.
    """
    m = await _api('fund/fundcompare', model=_Funds)
    assert m.totalCount <= m.pageSize
    df = _Df([vars(i) for i in m.items])
    _fix_website_address(df)
    return df


class _FundTypes(_BaseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[FundType]


class FundType(_BaseModel):
    fundType: int
    name: str
    isActive: bool


async def fund_types() -> _Df:
    """See funds.FundType for column names."""
    m = await _api('fund/fundtype', model=_FundTypes)
    assert m.totalCount <= m.pageSize
    return _Df([vars(i) for i in m.items])


class AverageReturns(_BaseModel):
    id: int
    fundTypeId: int
    netAsset: int | None
    stock: None | float
    bond: None | float
    cash: None | float
    deposit: None | float
    dailyEfficiency: None | float
    weeklyEfficiency: None | float
    monthlyEfficiency: None | float
    quarterlyEfficiency: None | float
    sixMonthEfficiency: None | float
    annualEfficiency: None | float
    efficiency: None | float


async def average_returns() -> _Df:
    """Return a Dataframe for https://www.fipiran.ir/mf/efficiency.

    See AverageReturns for column names.
    """
    m = await _api(
        'fund/averagereturns', model=_RootModel[list[AverageReturns]]
    )
    df = _Df(vars(i) for i in m.root)
    return df.astype({'netAsset': 'Int64'}, copy=False)


class _TreeMap(_BaseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[TreeMapItem]


class TreeMapItem(_CommonFundInfo):
    rankLastUpdate: _datetime
    fundType: int
    typeOfInvest: str
    fundSize: int
    dailyEfficiency: float
    weeklyEfficiency: float
    monthlyEfficiency: float
    quarterlyEfficiency: float
    sixMonthEfficiency: float
    annualEfficiency: float
    statisticalNav: float
    efficiency: float
    cancelNav: float
    issueNav: float
    dividendIntervalPeriod: int
    guaranteedEarningRate: None | int
    date: _datetime
    netAsset: int
    estimatedEarningRate: float | None
    investedUnits: int
    articlesOfAssociationLink: None
    prosoectusLink: None
    websiteAddress: list[str]
    manager: str
    managerSeoRegisterNo: None | str
    guarantorSeoRegisterNo: None | str
    auditor: str
    custodian: str
    guarantor: str
    beta: float | None
    alpha: float | None
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
    smallSymbolName: None = None
    insCode: None = None
    fundWatch: None


async def map_data() -> _Df:
    """See TreeMapItem for column names."""
    m = await _api('fund/treemap', model=_TreeMap)
    df = _Df(vars(i) for i in m.items)
    _fix_website_address(df)
    return df


class _DepData(_BaseModel):
    status: int
    message: str
    pageNumber: int
    pageSize: int
    totalCount: int
    items: list[DepItem]


class DepItem(_CommonFundInfo):
    fundType: int
    fundSize: int | None
    dailyEfficiency: None | float
    weeklyEfficiency: None | float
    monthlyEfficiency: None | float
    quarterlyEfficiency: None | float
    sixMonthEfficiency: None | float
    annualEfficiency: None | float
    efficiency: None | float
    cancelNav: None | float
    issueNav: None | float
    statisticalNav: None | float
    tempGuarantorName: None | str
    tempManagerName: str
    date: _datetime
    netAsset: int | None
    manager: None | Manager
    guarantor: Guarantor | None
    rankLastUpdate: _datetime
    typeOfInvest: str
    beta: None | float
    alpha: None | float
    dividendIntervalPeriod: int | None


class Manager(_BaseModel):
    managerId: int
    cfiId: int | None
    managerSeoRegisterNo: None | str
    name: str
    managerNationalCode: None | str
    type: int | None
    seoRegisterDate: None | _datetime
    registeredCapital: int | None
    webSite: None | str
    email: None | str
    ceo: None | str
    tel: None | str
    address: None | str
    nationalId: None | str
    registrationNumber: None | str
    registerPlace: None
    registerPlaceId: None
    registerDate: None | _datetime
    cfiLastModificationTime: None | _datetime
    isCompleted: bool


class Guarantor(_BaseModel):
    guarantorId: int
    cfiId: int | None
    guarantorSeoRegisterNo: str
    name: str
    guarantorNationalCode: None | str
    type: int | None
    seoRegisterDate: None | _datetime
    registeredCapital: int | None
    webSite: None | str
    email: None | str
    ceo: None | str
    tel: None | str
    address: None | str
    nationalId: None | str
    registrationNumber: None | str
    registerPlace: None
    registerPlaceId: None
    registerDate: None | _datetime
    cfiLastModificationTime: None | _datetime
    isCompleted: bool


async def dependency_graph_data() -> _Df:
    """See DepItem for column names."""
    m = await _api('fund/dependencygraph', model=_DepData)
    return _Df(vars(i) for i in m.items)
