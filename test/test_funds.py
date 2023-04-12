from aiohttp_test_utils import file
from numpy import dtype
from pandas import CategoricalDtype, Int64Dtype, StringDtype

from fipiran.funds import (
    Fund,
    average_returns,
    dependency_graph_data,
    funds,
    map_data,
)

fund = Fund(11215)
string = StringDtype()


def test_repr():
    assert repr(fund) == 'Fund(11215)'
    assert repr(Fund('11215')) == "Fund('11215')"


@file('portfoliochart_atlas.json')
async def test_asset_allocation_history():
    df = await fund.asset_allocation_history()
    assert [*df.dtypes.items()] == [
        ('date', dtype('<M8[ns]')),
        ('fiveBest', dtype('float64')),
        ('stock', dtype('float64')),
        ('bond', dtype('float64')),
        ('other', dtype('float64')),
        ('cash', dtype('float64')),
        ('deposit', dtype('float64')),
        ('fundUnit', dtype('O')),
        ('commodity', dtype('O'))
    ]

@file('getfundchart_atlas.json')
async def test_issue_cancel_history():
    df = await fund.issue_cancel_history(all_=False)
    assert [*df.dtypes.items()] == [
        ('issueNav', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('statisticalNav', dtype('float64'))]
    assert len(df) >= 360
    assert df.index.name == 'date'
    assert df.index.dtype == '<M8[ns]'


@file('getfundnetassetchart_atlas.json')
async def test_nav_history():
    df = await fund.nav_history(all_=False)
    assert [*df.dtypes.items()] == [
        ('netAsset', dtype('int64')),
        ('unitsSubDAY', dtype('int64')),
        ('unitsRedDAY', dtype('int64')),
    ]
    assert len(df) >= 360
    assert df.index.dtype == '<M8[ns]'


@file('getfund_atlas.json')
async def test_info():
    info = await fund.info()
    assert len(info) >= 63
    assert type(info) is dict


@file('fundcompare.json')
async def test_funds():
    df = await funds()
    assert len(df) > 300
    assert [*df.dtypes.items()] == [
        ('regNo', dtype('int64')),
        ('name', string),
        ('rankOf12Month', dtype('float64')),
        ('rankOf24Month', dtype('float64')),
        ('rankOf36Month', dtype('float64')),
        ('rankOf48Month', dtype('O')),
        ('rankOf60Month', dtype('float64')),
        ('rankLastUpdate', dtype('O')),
        ('fundType', dtype('int64')),
        (
            'typeOfInvest',
            CategoricalDtype(
                categories=['IssuanceAndCancellation', 'Negotiable'], ordered=False
            ),
        ),
        ('fundSize', dtype('float64')),
        ('initiationDate', dtype('O')),
        ('dailyEfficiency', dtype('float64')),
        ('weeklyEfficiency', dtype('float64')),
        ('monthlyEfficiency', dtype('float64')),
        ('quarterlyEfficiency', dtype('float64')),
        ('sixMonthEfficiency', dtype('float64')),
        ('annualEfficiency', dtype('float64')),
        ('statisticalNav', dtype('float64')),
        ('efficiency', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('issueNav', dtype('float64')),
        ('dividendIntervalPeriod', 'Int64'),
        ('guaranteedEarningRate', dtype('float64')),
        ('date', dtype('<M8[ns]')),
        ('netAsset', dtype('float64')),
        ('estimatedEarningRate', dtype('float64')),
        ('investedUnits', dtype('float64')),
        ('articlesOfAssociationLink', dtype('O')),
        ('prosoectusLink', dtype('O')),
        ('websiteAddress', string),
        ('manager', string),
        ('managerSeoRegisterNo', Int64Dtype()),
        ('guarantorSeoRegisterNo', Int64Dtype()),
        ('auditor', string),
        ('custodian', string),
        ('guarantor', string),
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
        ('isCompleted', dtype('bool')),
        ('fiveBest', dtype('float64')),
        ('stock', dtype('float64')),
        ('bond', dtype('float64')),
        ('other', dtype('float64')),
        ('cash', dtype('float64')),
        ('deposit', dtype('float64')),
        ('fundUnit', dtype('float64')),
        ('commodity', dtype('float64')),
        ('fundPublisher', dtype('int64')),
        ('fundWatch', dtype('O')),
    ]


@file('averagereturns.json')
async def test_average_returns():
    df = await average_returns()
    assert len(df) == 11
    assert [*df.dtypes.items()] == [
        ('id', dtype('int64')),
        ('fundTypeId', dtype('int64')),
        ('netAsset', Int64Dtype()),
        ('stock', dtype('float64')),
        ('bond', dtype('float64')),
        ('cash', dtype('float64')),
        ('deposit', dtype('float64')),
        ('dailyEfficiency', dtype('float64')),
        ('weeklyEfficiency', dtype('float64')),
        ('monthlyEfficiency', dtype('float64')),
        ('quarterlyEfficiency', dtype('float64')),
        ('sixMonthEfficiency', dtype('float64')),
        ('annualEfficiency', dtype('float64')),
        ('efficiency', dtype('float64'))
    ]


@file('treemap.json')
async def test_map_data():
    df = await map_data()
    assert [*df.dtypes.items()] == [
        ('regNo', dtype('int64')),
        ('name', string),
        ('rankOf12Month', dtype('float64')),
        ('rankOf24Month', dtype('float64')),
        ('rankOf36Month', dtype('float64')),
        ('rankOf48Month', dtype('O')),
        ('rankOf60Month', dtype('float64')),
        ('rankLastUpdate', dtype('O')),
        ('fundType', dtype('int64')),
        (
            'typeOfInvest',
            CategoricalDtype(
                categories=['IssuanceAndCancellation', 'Negotiable'], ordered=False
            ),
        ),
        ('fundSize', dtype('int64')),
        ('initiationDate', dtype('O')),
        ('dailyEfficiency', dtype('float64')),
        ('weeklyEfficiency', dtype('float64')),
        ('monthlyEfficiency', dtype('float64')),
        ('quarterlyEfficiency', dtype('float64')),
        ('sixMonthEfficiency', dtype('float64')),
        ('annualEfficiency', dtype('float64')),
        ('statisticalNav', dtype('float64')),
        ('efficiency', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('issueNav', dtype('float64')),
        ('dividendIntervalPeriod', Int64Dtype()),
        ('guaranteedEarningRate', dtype('float64')),
        ('date', dtype('<M8[ns]')),
        ('netAsset', dtype('int64')),
        ('estimatedEarningRate', dtype('float64')),
        ('investedUnits', dtype('int64')),
        ('articlesOfAssociationLink', dtype('O')),
        ('prosoectusLink', dtype('O')),
        ('websiteAddress', dtype('O')),
        ('manager', string),
        ('managerSeoRegisterNo', Int64Dtype()),
        ('guarantorSeoRegisterNo', Int64Dtype()),
        ('auditor', string),
        ('custodian', string),
        ('guarantor', string),
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
        ('isCompleted', dtype('bool')),
        ('fiveBest', dtype('float64')),
        ('stock', dtype('float64')),
        ('bond', dtype('float64')),
        ('other', dtype('float64')),
        ('cash', dtype('float64')),
        ('deposit', dtype('float64')),
        ('fundUnit', dtype('float64')),
        ('commodity', dtype('float64')),
        ('fundPublisher', dtype('int64')),
        ('fundWatch', dtype('O')),
    ]
    assert len(df) > 286


@file('dependencygraph.json')
async def test_dependency_graph_data():
    df = await dependency_graph_data()
    assert [*df.dtypes.items()] == [
        ('regNo', dtype('int64')),
        ('name', 'string[python]'),
        ('fundType', dtype('int64')),
        ('fundSize', Int64Dtype()),
        ('dailyEfficiency', dtype('float64')),
        ('weeklyEfficiency', dtype('float64')),
        ('monthlyEfficiency', dtype('float64')),
        ('quarterlyEfficiency', dtype('float64')),
        ('sixMonthEfficiency', dtype('float64')),
        ('annualEfficiency', dtype('float64')),
        ('efficiency', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('issueNav', dtype('float64')),
        ('statisticalNav', dtype('float64')),
        ('tempGuarantorName', dtype('O')),
        ('tempManagerName', dtype('O')),
        ('date', dtype('<M8[ns]')),
        ('netAsset', Int64Dtype()),
        ('manager', 'string[python]'),
        ('guarantor', 'string[python]'),
        ('rankOf12Month', dtype('float64')),
        ('rankOf24Month', dtype('float64')),
        ('rankOf36Month', dtype('float64')),
        ('rankOf48Month', dtype('O')),
        ('rankOf60Month', dtype('float64')),
        ('rankLastUpdate', dtype('O')),
        (
            'typeOfInvest',
            CategoricalDtype(
                categories=['IssuanceAndCancellation', 'Negotiable'], ordered=False
            ),
        ),
        ('initiationDate', dtype('O')),
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
        ('dividendIntervalPeriod', dtype('float64')),
    ]
    assert len(df) > 286


@file('alpha_beta.json')
async def test_alpha_beta():
    df = await fund.alpha_beta(all_=False)
    assert [*df.dtypes.items()] == [('beta', dtype('float64')), ('alpha', dtype('float64'))]
    assert df.index.name == 'date'
    assert df.index.dtype == dtype('<M8[ns]')
