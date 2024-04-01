from aiohutils.tests import file
from polars import (
    Boolean,
    DataFrame,
    Datetime,
    Float64,
    Int64,
    Null,
    String,
    Struct,
)

from fipiran.funds import (
    _KNOWN_DTYPES,  # noqa
    Fund,
    average_returns,
    dependency_graph_data,
    funds,
    map_data,
)

fund = Fund(11215)


def test_repr():
    assert repr(fund) == 'Fund(11215)'
    assert repr(Fund('11215')) == "Fund('11215')"


@file('portfoliochart_atlas.json')
async def test_asset_allocation_history():
    df = await fund.asset_allocation_history()
    assert [*zip(df.columns, df.dtypes)] == [
        ('date', Datetime(time_unit='us', time_zone=None)),
        ('fiveBest', Float64),
        ('stock', Float64),
        ('bond', Float64),
        ('other', Float64),
        ('cash', Float64),
        ('deposit', Float64),
        ('fundUnit', Null),
        ('commodity', Null),
    ]


@file('getfundchart_atlas.json')
async def test_navps():
    df = await fund.navps_history(all_=False)
    assert [*zip(df.columns, df.dtypes)] == [
        ('date', Datetime(time_unit='us', time_zone=None)),
        ('issueNav', Float64),
        ('cancelNav', Float64),
        ('statisticalNav', Float64),
    ]
    assert (df['cancelNav'] <= df['issueNav']).all()
    assert len(df) >= 360


@file('getfundnetassetchart_atlas.json')
async def test_nav_history():
    df = await fund.nav_history(all_=False)
    assert [*zip(df.columns, df.dtypes)] == [
        ('date', Datetime(time_unit='us', time_zone=None)),
        ('netAsset', Int64),
        ('unitsSubDAY', Int64),
        ('unitsRedDAY', Int64),
    ]
    assert len(df) >= 360


@file('getfund_atlas.json')
async def test_info():
    info = await fund.info()
    assert len(info) >= 63
    assert type(info) is dict  # noqa: E721


EXPECTED_INFERRED_DTYPES = {
    'articlesOfAssociationLink': Null,
    'auditor': String,
    'bond': Float64,
    'cash': Float64,
    'commodity': Float64,
    'custodian': String,
    'date': Datetime(time_unit='us', time_zone=None),
    'deposit': Float64,
    'estimatedEarningRate': Float64,
    'fiveBest': Float64,
    'fundPublisher': Int64,
    'fundUnit': Float64,
    'fundWatch': Null,
    'guaranteedEarningRate': Int64,
    'guarantor': (Struct, String),
    'initiationDate': String,
    'insCode': String,
    'isCompleted': Boolean,
    'manager': (Struct, String),
    'name': String,
    'other': Float64,
    'prosoectusLink': Null,
    'rankLastUpdate': String,
    'smallSymbolName': String,
    'stock': Float64,
    'tempGuarantorName': String,
    'tempManagerName': String,
    'websiteAddress': String,
}


def assert_dtypes(df: DataFrame):
    cols = {*df.columns}
    assert not cols - (_KNOWN_DTYPES.keys() | EXPECTED_INFERRED_DTYPES.keys())
    for col in cols & EXPECTED_INFERRED_DTYPES.keys():
        et = EXPECTED_INFERRED_DTYPES[col]
        try:
            if type(et) is tuple:
                assert df[col].dtype in et, f'{col=}'
            else:
                assert df[col].dtype == et, f'{col=}'
        except Exception:  # a good breakpoint
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
    assert [*zip(df.columns, df.dtypes)] == [
        ('id', Int64),
        ('fundTypeId', Int64),
        ('netAsset', Int64),
        ('stock', Float64),
        ('bond', Float64),
        ('cash', Float64),
        ('deposit', Float64),
        ('dailyEfficiency', Float64),
        ('weeklyEfficiency', Float64),
        ('monthlyEfficiency', Float64),
        ('quarterlyEfficiency', Float64),
        ('sixMonthEfficiency', Float64),
        ('annualEfficiency', Float64),
        ('efficiency', Float64),
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
    assert [*zip(df.columns, df.dtypes)] == [
        ('date', Datetime(time_unit='us', time_zone=None)),
        ('beta', Float64),
        ('alpha', Float64),
    ]
