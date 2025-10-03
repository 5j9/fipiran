from aiohutils.tests import file
from numpy import dtype
from pandas import DataFrame, Int64Dtype

from fipiran.funds import (
    DepItem,
    Fund,
    FundInfo,
    SpecificFundInfo,
    TreeMapItem,
    _CommonFundInfo,
    average_returns,
    dependency_graph_data,
    fund_types,
    funds,
    map_data,
)

_str = 'string'
_KNOWN_DTYPES = {
    # 'initiationDate': 'datetime64', fails on some funds
    'alpha': 'float64',
    'annualEfficiency': 'float64',
    'auditor': _str,
    'beta': 'float64',
    'cancelNav': 'float64',
    'custodian': _str,
    'dailyEfficiency': 'float64',
    # date cannot be set using astype, see:
    # https://github.com/pandas-dev/pandas/issues/53127
    'date': 'O',
    'dividendIntervalPeriod': 'Int64',
    'efficiency': 'float64',
    'fundSize': 'Int64',
    'fundType': 'int64',
    'guarantor': _str,
    'guarantorSeoRegisterNo': 'Int64',
    'initiationDate': 'O',
    'insCode': _str,
    'investedUnits': 'Int64',
    'issueNav': 'float64',
    'manager': _str,
    'managerSeoRegisterNo': 'Int64',
    'monthlyEfficiency': 'float64',
    'name': _str,
    'netAsset': 'Int64',
    'quarterlyEfficiency': 'float64',
    'rankLastUpdate': 'O',
    'rankOf12Month': 'float64',
    'rankOf24Month': 'float64',
    'rankOf36Month': 'float64',
    'rankOf48Month': 'float64',
    'rankOf60Month': 'float64',
    'regNo': _str,
    'sixMonthEfficiency': 'float64',
    'smallSymbolName': _str,
    'statisticalNav': 'float64',
    'tempGuarantorName': _str,
    'tempManagerName': _str,
    'typeOfInvest': 'category',
    'weeklyEfficiency': 'float64',
}

fund = Fund(11215)


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
    assert len(vars(info)) >= 63
    assert type(info) is SpecificFundInfo
    unexpected_fields = (
        vars(info).keys() - SpecificFundInfo.__pydantic_fields__.keys()
    )
    assert not unexpected_fields


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
    'guaranteedEarningRate': None,
    'isCompleted': bool,
    'other': 'float64',
    'prosoectusLink': None,
    'stock': None,
    'websiteAddress': _str,
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
                assert df[col].dtype == et, f'{col=} {df[col].dtype=} {et=}'
        except:  # a good breakpoint
            raise


@file('fundcompare.json')
async def test_funds():
    df = await funds()
    assert len(df) > 300
    unexpected_fields = set(df.columns) - FundInfo.__pydantic_fields__.keys()
    assert not unexpected_fields
    assert_dtypes(df)


@file('averagereturns.json')
async def test_average_returns():
    df = await average_returns()
    assert len(df) >= 11
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
    unexpected_fields = (
        set(df.columns) - TreeMapItem.__pydantic_fields__.keys()
    )
    assert not unexpected_fields


@file('dependencygraph.json')
async def test_dependency_graph_data():
    df = await dependency_graph_data()
    assert_dtypes(df)
    assert len(df) > 286
    unexpeced_keys = set(df.columns) - DepItem.__pydantic_fields__.keys()
    assert not unexpeced_keys


@file('alpha_beta.json')
async def test_alpha_beta():
    df = await fund.alpha_beta(all_=False)
    assert [*df.dtypes.items()] == [
        ('beta', dtype('float64')),
        ('alpha', dtype('float64')),
    ]
    assert df.index.name == 'date'
    assert df.index.dtype == dtype('<M8[ns]')


@file('fund_types.json')
async def test_fund_types():
    df = await fund_types()
    assert [*df.dtypes.items()] == [
        ('fundType', dtype('int64')),
        ('name', _str),
        ('isActive', dtype('bool')),
    ]


def test_common_fund_info_fields():
    """
    Tests that no subclass of _CommonFundInfo redefines a field already
    defined in the base class. And asserts that no field is common among
    the direct subclasses; such fields should be moved to the base class.
    """
    parent_fields = set(_CommonFundInfo.__pydantic_fields__.keys())

    # Use a dictionary to store the directly defined fields for each subclass
    subclass_fields: dict[str, set] = {}

    for subclass in _CommonFundInfo.__subclasses__():
        # Get fields defined directly on the subclass (not inherited)
        subclass_directly_defined_fields = set(subclass.__annotations__.keys())

        # --- PART 1: Check for redefined fields in the parent ---
        redefined_fields = parent_fields & subclass_directly_defined_fields
        assert not redefined_fields, (
            f'Subclass {subclass.__name__} illegally redefines fields already in '
            f'_CommonFundInfo: {redefined_fields}'
        )

        # Store the directly defined fields for Part 2
        subclass_fields[subclass.__name__] = subclass_directly_defined_fields

    # --- PART 2: Check for common fields among all subclasses ---
    # Start with the fields of the first subclass as the initial 'common' set
    # and then find the intersection with all subsequent subclasses.

    # Get a list of the sets of fields
    all_subclass_field_sets = list(subclass_fields.values())

    if not all_subclass_field_sets:
        # No subclasses found, nothing to check for commonality
        return

    # Initialize the common_fields set with the first set
    common_fields = all_subclass_field_sets[0]

    # Iterate through the rest of the sets to find the intersection
    for field_set in all_subclass_field_sets[1:]:
        common_fields = common_fields & field_set

    # Types are different for these two fields. Redefinition is unavoidable.
    common_fields -= {'guarantor', 'manager'}

    assert not common_fields, (
        f'The following fields are common among all subclasses and should be '
        f'moved to the base class _CommonFundInfo: {common_fields}'
    )
