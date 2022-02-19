from numpy import dtype
from pandas import CategoricalDtype, Series, DataFrame
from pandas.testing import assert_series_equal

from fipiran.funds import Fund, dependency_graph_data, funds, average_returns, map_data
from . import disable_get, patch_get


def setup_module():
    disable_get.start()


def teardown_module():
    disable_get.stop()


fund = Fund(11215)


def test_repr():
    assert repr(fund) == 'Fund(11215)'
    assert repr(Fund('11215')) == "Fund('11215')"


@patch_get('getfundchartasset_atlas.json')
def test_asset_allocation():
    d = fund.asset_allocation()
    del d['fiveBest']
    assert sum(d.values()) == 100


@patch_get('getfundchart_atlas.json')
def test_issue_cancel_history():
    df = fund.issue_cancel_history()
    assert_series_equal(
        df.dtypes, Series(['float64', 'float64'], ['issueNav', 'cancelNav'])
    )
    assert len(df) == 366
    assert df.index.dtype == '<M8[ns]'


@patch_get('getfundnetassetchart_atlas.json')
def test_nav_history():
    df = fund.nav_history()
    assert [*df.dtypes.items()] == [
        ('netAsset', dtype('int64')),
        ('unitsSubDAY', dtype('int64')),
        ('unitsRedDAY', dtype('int64')),
    ]
    assert len(df) == 366
    assert df.index.dtype == '<M8[ns]'


@patch_get('getfund_atlas.json')
def test_info():
    info = fund.info()
    assert len(info) == 63
    assert type(info) is dict


@patch_get('fundcompare.json')
def test_funds():
    df = funds()
    assert len(df) > 300
    assert [*df.dtypes.items()] == [
        ('regNo', dtype('int64')),
        ('name', 'string'),
        ('rankOf12Month', dtype('int64')),
        ('rankOf36Month', dtype('int64')),
        ('rankOf60Month', dtype('int64')),
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
        ('dividendIntervalPeriod', dtype('float64')),
        ('guaranteedEarningRate', dtype('O')),
        ('date', dtype('<M8[ns]')),
        ('netAsset', dtype('float64')),
        ('estimatedEarningRate', dtype('float64')),
        ('investedUnits', dtype('float64')),
        ('articlesOfAssociationLink', dtype('O')),
        ('prosoectusLink', dtype('O')),
        ('websiteAddress', dtype('O')),
        ('manager', 'string'),
        ('auditor', 'string'),
        ('custodian', 'string'),
        ('guarantor', 'string'),
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
        ('isCompleted', dtype('bool')),
        ('fundWatch', dtype('O')),
    ]


@patch_get('MFBazdehAVG.html')
def test_average_returns():
    df = average_returns()
    assert len(df) == 4
    assert [*df.dtypes.items()] == [
        ('نوع صندوق', dtype('O')),
        ('خالص ارزش دارایی صندوق(میلیارد ریال)', dtype('int64')),
        ('%میانگین دارایی\u200cهای نقدی', dtype('float64')),
        ('میانگین بازدهی هفته(%)', dtype('float64')),
        ('میانگین بازدهی ماه(%)', dtype('float64')),
        ('میانگین بازدهی 3 ماهه(%)', dtype('float64')),
        ('میانگین بازدهی 6 ماهه(%)', dtype('float64')),
        ('میانگین بازدهی سال(%)', dtype('float64')),
        ('میانگین بازدهی از آغاز فعالیت(%)', dtype('float64')),
    ]


@patch_get('treemap.json')
def test_map_data():
    df = map_data()
    assert [*df.dtypes.items()] == [
        ('regNo', dtype('int64')),
        ('name', 'string[python]'),
        ('rankOf12Month', dtype('int64')),
        ('rankOf36Month', dtype('int64')),
        ('rankOf60Month', dtype('int64')),
        ('rankLastUpdate', dtype('O')),
        ('fundType', dtype('int64')),
        (
            'typeOfInvest',
            CategoricalDtype(
                categories=['IssuanceAndCancellation', 'Negotiable'], ordered=False
            ),
        ),
        ('fundSize', dtype('int64')),
        ('initiationDate', dtype('<M8[ns]')),
        ('dailyEfficiency', dtype('float64')),
        ('weeklyEfficiency', dtype('float64')),
        ('monthlyEfficiency', dtype('float64')),
        ('quarterlyEfficiency', dtype('float64')),
        ('sixMonthEfficiency', dtype('float64')),
        ('annualEfficiency', dtype('float64')),
        ('statisticalNav', dtype('O')),
        ('efficiency', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('issueNav', dtype('float64')),
        ('dividendIntervalPeriod', dtype('float64')),
        ('guaranteedEarningRate', dtype('O')),
        ('date', dtype('<M8[ns]')),
        ('netAsset', dtype('int64')),
        ('estimatedEarningRate', dtype('float64')),
        ('investedUnits', dtype('int64')),
        ('articlesOfAssociationLink', dtype('O')),
        ('prosoectusLink', dtype('O')),
        ('websiteAddress', dtype('O')),
        ('manager', 'string[python]'),
        ('auditor', 'string[python]'),
        ('custodian', 'string[python]'),
        ('guarantor', 'string[python]'),
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
        ('isCompleted', dtype('bool')),
        ('fundWatch', dtype('O')),
    ]
    assert len(df) > 286


@patch_get('dependencygraph.json')
def test_dependency_graph_data():
    df = dependency_graph_data()
    assert [*df.dtypes.items()] == [
        ('regNo', dtype('int64')),
        ('name', 'string[python]'),
        ('fundType', dtype('int64')),
        ('fundSize', dtype('int64')),
        ('dailyEfficiency', dtype('float64')),
        ('weeklyEfficiency', dtype('float64')),
        ('monthlyEfficiency', dtype('float64')),
        ('quarterlyEfficiency', dtype('float64')),
        ('sixMonthEfficiency', dtype('float64')),
        ('annualEfficiency', dtype('float64')),
        ('efficiency', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('issueNav', dtype('float64')),
        ('date', dtype('<M8[ns]')),
        ('netAsset', dtype('int64')),
        ('managerId', dtype('int64')),
        ('manager', 'string[python]'),
        ('managerCode', 'string[python]'),
        ('guarantorId', dtype('float64')),
        ('guarantor', 'string[python]'),
        ('guarantorCode', 'string[python]'),
        ('rankOf12Month', dtype('int64')),
        ('rankOf36Month', dtype('int64')),
        ('rankOf60Month', dtype('int64')),
        ('rankLastUpdate', dtype('O')),
        (
            'typeOfInvest',
            CategoricalDtype(
                categories=['IssuanceAndCancellation', 'Negotiable'], ordered=False
            ),
        ),
        ('initiationDate', dtype('<M8[ns]')),
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
    ]
    assert len(df) > 286
