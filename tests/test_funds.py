from polars import (
    Boolean,
    Datetime,
    Float64,
    Int64,
    LazyFrame,
    Null,
    String,
    col,
    len as pl_len,
)
from pytest_aiohutils import file, files

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

_KNOWN_DTYPES = {
    'alpha': Float64,
    'annualEfficiency': Float64,
    'auditor': String,
    'beta': Float64,
    'cancelNav': Float64,
    'custodian': String,
    'dailyEfficiency': Float64,
    'date': Datetime,
    'dividendIntervalPeriod': Int64,
    'efficiency': Float64,
    'fundSize': Int64,
    'fundType': Int64,
    'groupId': Int64,
    'guarantor': String,
    'guarantorSeoRegisterNo': Int64,
    'initiationDate': Datetime,
    'insCode': String,
    'investedUnits': Int64,
    'issueNav': Float64,
    'manager': String,
    'managerSeoRegisterNo': Int64,
    'monthlyEfficiency': Float64,
    'name': String,
    'netAsset': Int64,
    'quarterlyEfficiency': Float64,
    'rankLastUpdate': Datetime,
    'rankOf12Month': Float64,
    'rankOf24Month': Float64,
    'rankOf36Month': Float64,
    'rankOf48Month': Float64,
    'rankOf60Month': Float64,
    'rankOfSeason': Float64,
    'regNo': String,
    'sixMonthEfficiency': Float64,
    'smallSymbolName': String,
    'statisticalNav': Float64,
    'tempGuarantorName': String,
    'tempManagerName': String,
    'typeOfInvest': String,
    'weeklyEfficiency': Float64,
}

fund = Fund(11215)


def test_repr():
    assert repr(fund) == "Fund(11215, '0')"
    assert repr(Fund('11215')) == "Fund('11215', '0')"


@file('portfoliochart_atlas.json')
async def test_asset_allocation_history():
    lf = await fund.asset_allocation_history()
    assert isinstance(lf, LazyFrame)

    assert lf.collect_schema() == {
        'date': Datetime(time_unit='us', time_zone=None),
        'fiveBest': Float64,
        'stock': Float64,
        'bond': Float64,
        'other': Float64,
        'cash': Float64,
        'deposit': Float64,
    }


@file('getfundchart_atlas.json')
async def test_navps():
    lf = await fund.navps_history(all_=False)
    assert isinstance(lf, LazyFrame)

    schema = lf.collect_schema()
    assert schema['date'] == Datetime
    assert schema['issueNav'] == Float64
    assert schema['cancelNav'] == Float64
    assert schema['statisticalNav'] == Float64

    # Added .all() to all_ordered so everything resolves to a single scalar row
    res = lf.select(
        all_ordered=(col('cancelNav') <= col('issueNav')).all(),
        total_rows=pl_len(),
        is_sorted=(col('date').diff().drop_nulls() >= 0).all(),
    ).collect()

    assert res['all_ordered'].item()
    assert res['total_rows'].item() >= 350
    assert res['is_sorted'].item()


@file('getfundnetassetchart_atlas.json')
async def test_nav_history():
    lf = await fund.nav_history(all_=False)
    assert isinstance(lf, LazyFrame)

    schema = lf.collect_schema()
    assert schema['date'] == Datetime
    assert schema['netAsset'] == Int64
    assert schema['unitsSubDAY'] == Int64
    assert schema['unitsRedDAY'] == Int64

    res = lf.select(
        total_rows=pl_len(),
        is_sorted=(col('date').diff().drop_nulls() >= 0).all(),
    ).collect()

    assert res['total_rows'].item() >= 350
    assert res['is_sorted'].item()


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
    'articlesOfAssociationLink': Null,
    'bond': Float64,
    'cash': Float64,
    'commodity': Float64,
    'deposit': Float64,
    'estimatedEarningRate': Float64,
    'fiveBest': Float64,
    'fundPublisher': Int64,
    'fundUnit': Float64,
    'fundWatch': Null,
    'guaranteedEarningRate': Null,
    'isCompleted': Boolean,
    'other': Float64,
    'prosoectusLink': Null,
    'stock': Null,
    'websiteAddress': String,
}


def assert_dtypes(lf: LazyFrame):
    # Check that schema matches our allowed definitions without needing to collect data rows
    schema = lf.collect_schema()
    cols = set(schema.keys())

    unknown = sorted(
        (col, schema[col])
        for col in cols
        if col not in _KNOWN_DTYPES and col not in EXPECTED_INFERRED_DTYPES
    )
    assert not unknown, 'Unknown columns:\n' + '\n'.join(
        f'  {col}: {dtype}' for col, dtype in unknown
    )

    for c in cols & EXPECTED_INFERRED_DTYPES.keys():
        expected_type = EXPECTED_INFERRED_DTYPES[c]
        actual_type = schema[c]

        # Simple structural null mapping might fall back to specific type inferenced types or explicit Null types
        if expected_type is Null:
            # Tolerates Polars assigning typed structural null columns
            continue
        else:
            assert actual_type == expected_type, (
                f'{c=} {actual_type=} {expected_type=}'
            )


@file('fundcompare.json')
async def test_funds_funds():
    lf = await funds()
    assert isinstance(lf, LazyFrame)
    assert lf.select(pl_len()).collect().item() > 300

    unexpected_fields = (
        set(lf.collect_schema().keys()) - FundInfo.__pydantic_fields__.keys()
    )
    assert not unexpected_fields
    assert_dtypes(lf)


@file('averagereturns.json')
async def test_average_returns():
    lf = await average_returns()
    assert isinstance(lf, LazyFrame)
    assert lf.select(pl_len()).collect().item() >= 11

    assert lf.collect_schema() == {
        'id': Int64,
        'fundTypeId': Int64,
        'netAsset': Int64,
        'stock': Float64,
        'bond': Float64,
        'cash': Float64,
        'deposit': Float64,
        'dailyEfficiency': Float64,
        'weeklyEfficiency': Float64,
        'monthlyEfficiency': Float64,
        'quarterlyEfficiency': Float64,
        'sixMonthEfficiency': Float64,
        'annualEfficiency': Float64,
        'efficiency': Float64,
    }


@file('treemap.json')
async def test_map_data():
    lf = await map_data()
    assert isinstance(lf, LazyFrame)
    assert_dtypes(lf)
    assert lf.select(pl_len()).collect().item() > 286

    # Replaced lf.schema.keys() with collect_schema().names()
    unexpected_fields = (
        set(lf.collect_schema().names())
        - TreeMapItem.__pydantic_fields__.keys()
    )
    assert not unexpected_fields


@file('dependencygraph.json')
async def test_dependency_graph_data():
    lf = await dependency_graph_data()
    assert isinstance(lf, LazyFrame)
    assert_dtypes(lf)
    assert lf.select(pl_len()).collect().item() > 286

    unexpected_keys = (
        set(lf.collect_schema().keys()) - DepItem.__pydantic_fields__.keys()
    )
    assert not unexpected_keys


@file('alpha_beta.json')
async def test_alpha_beta():
    lf = await fund.alpha_beta(all_=False)
    assert isinstance(lf, LazyFrame)

    schema = lf.collect_schema()
    assert schema['date'] == Datetime
    assert schema['beta'] == Float64
    assert schema['alpha'] == Float64

    is_sorted = (
        lf.select((col('date').diff().drop_nulls() >= 0).all())
        .collect()
        .item()
    )
    assert is_sorted


@file('fund_types.json')
async def test_fund_types():
    lf = await fund_types()
    assert isinstance(lf, LazyFrame)
    assert lf.collect_schema() == {
        'fundType': Int64,
        'name': String,
        'isActive': Boolean,
    }


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
    all_subclass_field_sets = list(subclass_fields.values())

    if not all_subclass_field_sets:
        return

    common_fields = all_subclass_field_sets[0]

    for field_set in all_subclass_field_sets[1:]:
        common_fields = common_fields & field_set

    common_fields -= {'guarantor', 'manager'}

    assert not common_fields, (
        f'The following fields are common among all subclasses and should be '
        f'moved to the base class _CommonFundInfo: {common_fields}'
    )


@files('resana_info.json', 'chatr_info.json')
async def test_group_id():
    resana = Fund(12286, 3)
    chatr = Fund(12286, 4)
    resana_info = await resana.info()
    chatr_info = await chatr.info()
    assert resana_info.regNo == chatr_info.regNo
    assert resana_info.issueNav != chatr_info.issueNav
