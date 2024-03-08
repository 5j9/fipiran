from aiohutils.tests import file
from numpy import dtype
from pandas import DataFrame, Int64Dtype, StringDtype

from fipiran.funds import (
    _KNOWN_DTYPES,  # noqa
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
        ('commodity', dtype('O')),
    ]


@file('getfundchart_atlas.json')
async def test_navps():
    df = await fund.navps_history(all_=False)
    assert [*df.dtypes.items()] == [
        ('issueNav', dtype('float64')),
        ('cancelNav', dtype('float64')),
        ('statisticalNav', dtype('float64')),
    ]
    assert (df['cancelNav'] <= df['issueNav']).all()
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
    assert type(info) is dict  # noqa: E721


EXPECTED_INFERRED_DTYPES = {
    'articlesOfAssociationLink': None,
    'bond': 'float64',
    'cash': 'float64',
    'commodity': 'float64',
    'deposit': 'float64',
    'estimatedEarningRate': 'float64',
    'fiveBest': 'float64',
    'fundPublisher': 'int64',
    'fundUnit': 'float64',
    'fundWatch': None,
    'guaranteedEarningRate': 'float64',
    'isCompleted': bool,
    'other': 'float64',
    'prosoectusLink': None,
    'stock': None,
    'websiteAddress': 'string',
}


def assert_dtypes(df: DataFrame):
    cols = {*df.columns}
    assert not cols - (_KNOWN_DTYPES.keys() | EXPECTED_INFERRED_DTYPES.keys())
    for col in cols & EXPECTED_INFERRED_DTYPES.keys():
        et = EXPECTED_INFERRED_DTYPES[col]
        try:
            if et is None:
                df[col].isna().all()
            else:
                assert df[col].dtype == et, f'{col=}'
        except:  # a good breakpoint
            raise


@file('fundcompare.json')
async def test_funds():
    df = await funds()
    assert len(df) > 300
    assert_dtypes(df)


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
        ('efficiency', dtype('float64')),
    ]


@file('treemap.json')
async def test_map_data():
    df = await map_data()
    assert_dtypes(df)
    assert len(df) > 286


@file('dependencygraph.json')
async def test_dependency_graph_data():
    df = await dependency_graph_data()
    assert_dtypes(df)
    assert len(df) > 286


@file('alpha_beta.json')
async def test_alpha_beta():
    df = await fund.alpha_beta(all_=False)
    assert [*df.dtypes.items()] == [
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
    ]
    assert df.index.name == 'date'
    assert df.index.dtype == dtype('<M8[ns]')
