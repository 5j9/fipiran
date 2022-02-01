from json import loads
from unittest.mock import patch

from jdatetime import datetime as jdatetime
from numpy import dtype, nan
from pandas import CategoricalDtype, Series, DataFrame, Timestamp
from pandas.testing import assert_series_equal
from pytest import raises

from fipiran.funds import Fund, dependency_graph_data, funds, average_returns, map_data
from fipiran.symbols import Symbol, search
from fipiran.data_service import (
    auto_complete_symbol,
    balance_sheet,
    export_symbol,
    auto_complete_fund,
    auto_complete_index,
    export_index,
    profit_loss,
)


disable_get = patch(
    'fipiran._get',
    side_effect=ConnectionError('_get should not be called during tests'),
)


def setup_module():
    disable_get.start()


def teardown_module():
    disable_get.stop()


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def json(self):
        return loads(self.content)


def patch_get(filename):
    with open(f'{__file__}/../testdata/{filename}', 'rb') as f:
        content = f.read()

    def fake_get(*_, **__):
        return FakeResponse(content)

    return patch('fipiran._get', fake_get)


fp = Fund(11215)


def test_repr():
    assert repr(fp) == 'Fund(11215)'
    assert repr(Fund('11215')) == "Fund('11215')"


@patch_get('getfundchartasset_atlas.json')
def test_asset_allocation():
    d = fp.asset_allocation()
    del d['fiveBest']
    assert sum(d.values()) == 100


@patch_get('getfundchart_atlas.json')
def test_issue_cancel_history():
    df = fp.issue_cancel_history()
    assert_series_equal(
        df.dtypes, Series(['float64', 'float64'], ['issueNav', 'cancelNav'])
    )
    assert len(df) == 366
    assert df.index.dtype == '<M8[ns]'


@patch_get('getfundnetassetchart_atlas.json')
def test_nav_history():
    df = fp.nav_history()
    assert_series_equal(df.dtypes, Series(['int64'], ['netAsset']))
    assert len(df) == 366
    assert df.index.dtype == '<M8[ns]'


@patch_get('getfund_atlas.json')
def test_info():
    info = fp.info()
    assert len(info) == 54
    assert type(info) is dict


@patch_get('fundcompare.json')
def test_funds():
    df = funds()
    assert len(df) == 307
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


@patch_get('autocomplete_arzesh.html')
def test_search():
    symbols = search('ارزش')
    assert symbols == [
        Symbol('وآفر'),
        Symbol('وارزش'),
        Symbol('وآفر'),
        Symbol('ارزش'),
        Symbol('ومدير'),
    ]
    assert symbols[3].l30 == 'صندوق س ارزش آفرين بيدار-سهام'


def test_symbol_from_name():
    assert f'{Symbol("فملی")!r}' == "Symbol('فملی')"


@patch_get('SymbolFMelli.html')
def test_inscode_cache():
    s = Symbol("فملی")
    assert s._inscode is None
    assert s.inscode == 35425587644337450
    assert s._inscode == 35425587644337450


@patch_get('priceDataFMelli.html')
def test_symbol_price_data():
    s = Symbol('فملی', 35425587644337450)
    assert s.price_data() == {
        'PriceMin': 13140.0,
        'PriceMax': 13770.0,
        'PDrCotVal': 13290.0,
        'PriceFirst': 13770.0,
        'PClosing': 13300.0,
        'changepdr': -1.77,
        'changepc': -1.7,
        'prevPrice': 13530.0,
        'ZTotTran': 10103.0,
        'QTotTran5J': 71934487.0,
        'QTotCap': 956433812420.0,
        'Deven': jdatetime(1400, 8, 1, 12, 30),
        'tmin': 12860.0,
        'tmax': 14200.0,
    }


@patch_get('BestLimitDataFMelli.html')
def test_symbol_best_limit_data():
    d1, d2 = Symbol('فملی', 35425587644337450).best_limit_data()
    assert type(d1) is type(d2) is DataFrame


@patch_get('RefrenceDataFmelli.html')
def test_symbol_refrence_data():
    assert Symbol('فملی', 35425587644337450).reference_data() == {
        'نام نماد': 'فملی',
        'نام شرکت': 'ملی\u200c صنایع\u200c مس\u200c ایران\u200c\u200c',
        'نام صنعت': 'فلزات اساسی',
        'وضعیت': 'مجاز',
        'بازار': 'بورس-بازاراول-تابلو اصلی',
        'حجم مبنا': '8869180',
        'کد معاملاتی نماد': 'IRO1MSMI0001',
    }


@patch_get('statistic30Fmelli.html')
def test_symbol_refrence_data():
    assert type(Symbol('فملی', 35425587644337450).statistic(30)) is DataFrame


@patch_get('CompanyInfoIndexSarv.html')
def test_company_info():
    assert Symbol('سرو', 64942549055019553).company_info() == {
        'نام نماد': 'سرو',
        'نام شرکت': 'صندوق سرمایه گذاری سرو سودمند مدبران',
        'مدیر عامل': 'رضا درخشان فر',
        'تلفن': '021-26231274',
        'فکس': '',
        'آدرس': '',
        'وب سایت': '',
        'ایمیل': '',
        'سال مالی': '09/30',
        'موضوع فعالیت': (
            'موضوع فعالیت صندوق، سرمایه\u200cگذاری در انواع اوراق'
            ' بهادار از جمله سهام و حق تقدم'
            ' سهام پذیرفته¬شده در بورس تهران و '
            'فرابورس ایران، گواهی سپرده کالایی،'
            ' اوراق بهادار با درآمد ثابت، سپرده\u200cها و گواهی¬های'
            ' سپردۀ بانکی است.'
        ),
    }


@patch_get('MFBazdehAVG.html')
def test_average_returns():
    df = average_returns()
    assert type(df) is DataFrame
    assert len(df) == 4
    assert df.query('`نوع صندوق` == "در سهام"')['میانگین بازدهی سال(%)'][0] == 28.4


@patch_get('AutoCompleteFundAva.json')
def test_auto_complete_fund():
    assert auto_complete_fund('آوا') == [
        {'RegNo': 11477, 'Name': 'آوای سهام کیان'},
        {'RegNo': 11884, 'Name': 'بازارگردانی آوای زاگرس'},
        {'RegNo': 11729, 'Name': 'قابل معامله آوای معیار'},
        {'RegNo': 11776, 'Name': 'صندوق سرمایه گذاری آوای فردای زاگرس'},
    ]


@patch_get('AutoCompleteindexHamVazn.json')
def test_auto_complete_index():
    assert auto_complete_index('هم وزن') == [
        {'LVal30': 'شاخص كل (هم وزن)', 'InstrumentID': 'IRX6XTPI0026'},
        {'LVal30': 'شاخص قيمت (هم وزن)', 'InstrumentID': 'IRXYXTPI0026'},
        {'LVal30': 'شاخص كل هم وزن فرابورس', 'InstrumentID': 'IRXZXOCI0026'},
    ]


@patch_get('ExportIndexHamVazn.xls.html')
def test_export_index():
    df = export_index('شاخص كل (هم وزن)', 14000101, 15000101, 'IRX6XTPI0026')
    assert df.iloc[-1].to_list() == ['شاخص', jdatetime(1400, 1, 8, 0, 0), 442552.0]


@patch('fipiran.data_service.auto_complete_index', side_effect=NotImplementedError)
def test_export_index_no_instrument_id(mock):
    with raises(NotImplementedError):
        export_index('هم وزن', 14000101, 15000101)
    mock.assert_called_once_with('هم وزن')


@patch_get('AutoCompleteSymbolMadira.json')
def test_auto_complete_symbol():
    assert auto_complete_symbol('مادیرا') == [
        {'LVal18AFC': 'ماديرا', 'InstrumentID': 'IRO3IOMZ0001'},
        {'LVal18AFC': 'ماديرا', 'InstrumentID': 'IRO7IOMZ0001'},
        {'LVal18AFC': 'ماديراح', 'InstrumentID': 'IRR3IOMZ0101'},
    ]


@patch_get('ExportSymbolMadira.xls.html')
def test_export_symbol():
    df = export_symbol('ماديرا', 14000801, 15000101, 'IRO3IOMZ0001')
    # noinspection PyTypeChecker
    assert df.iloc[-1].to_list() == [
        'مادیرا',
        jdatetime(1400, 8, 1, 0, 0),
        Timestamp('2021-10-23 00:00:00'),
        373.0,
        4505128.0,
        32545145672.0,
        7224.0,
        7224.0,
        7224.0,
        7230.0,
        7224.0,
        7604.0,
    ]


@patch('fipiran.data_service.auto_complete_symbol', side_effect=NotImplementedError)
def test_export_symbol_no_instrument_id(mock):
    with raises(NotImplementedError):
        export_symbol('ماديرا', 14000801, 15000101)
    mock.assert_called_once_with('ماديرا')


@patch_get('HistoryPricePaging_sarv.json')
def test_price_history():
    ph = Symbol('سرو').price_history(rows=3)
    data = ph['data']
    assert len(data) == 3
    assert [*data.dtypes.items()] == [
        ('DEven', dtype('O')),
        ('ZTotTran', dtype('float64')),
        ('QTotTran5J', dtype('float64')),
        ('QTotCap', dtype('float64')),
        ('PClosing', dtype('float64')),
        ('PcCh', dtype('float64')),
        ('PcChPercent', dtype('float64')),
        ('PDrCotVal', dtype('float64')),
        ('LTPCh', dtype('float64')),
        ('LTPChPercent', dtype('float64')),
        ('PriceYesterday', dtype('float64')),
        ('PriceMin', dtype('float64')),
        ('PriceMax', dtype('float64')),
        ('PriceFirst', dtype('float64')),
    ]
    assert data.index.dtype == dtype('<M8[ns]')
    assert ph['records'] == 599
    assert ph['total'] == 199


@patch('fipiran.symbols._fipiran', side_effect=NotImplementedError)
def test_price_history_url(get_mock):
    with raises(NotImplementedError):
        # l18 uses persian ی and ک
        Symbol('دارا یکم').price_history()
    get_mock.assert_called_once_with(  # needs to be called with arabic ي and ك
        'Symbol/HistoryPricePaging?symbolpara=دارا يكم&rows=365&page=1', json_resp=True
    )


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
    assert len(df) == 287


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
    assert len(df) == 287


@patch_get('BS_Fmelli_1394.xls')
def test_balance_sheet():
    df = balance_sheet('فملی', 1394)
    assert len(df) == 11
    assert [*df.dtypes.items()] == [
        ('Symbol', dtype('O')),
        ('PublishDate', dtype('O')),
        ('FinanceYear', dtype('O')),
        ('Year', dtype('int64')),
        ('period', dtype('int64')),
        ('IsAudit', dtype('float64')),
        ('cash', dtype('int64')),
        ('NetReceivables', dtype('int64')),
        ('OtherReceivables', dtype('int64')),
        ('ShortTermInvestments', dtype('int64')),
        ('Inventory', dtype('int64')),
        ('PrePayment', dtype('int64')),
        ('TotalCurrentAssets', dtype('int64')),
        ('LongTermInvestments', dtype('int64')),
        ('PropertyPlantAndEquipment', dtype('int64')),
        ('IntangibleAssets', dtype('int64')),
        ('TotalAssets', dtype('int64')),
        ('AccountsPayable', dtype('int64')),
        ('OtherPayable', dtype('int64')),
        ('PreRecive', dtype('int64')),
        ('TotalCurrentLiabilities', dtype('int64')),
        ('TotalLiabilities', dtype('int64')),
        ('capital', dtype('int64')),
        ('RetainedEarnings', dtype('int64')),
        ('TotalStockholderEquity', dtype('int64')),
    ]
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime  # noqa


@patch_get('IS_Fmelli_1394.xls')
def test_profit_loss():
    df = profit_loss('فملی', 1394)
    assert len(df) == 14
    assert [*df.dtypes.items()] == [
        ('Symbol', dtype('O')),
        ('publishDate', dtype('O')),
        ('FinanceYear', dtype('O')),
        ('Year', dtype('int64')),
        ('priod', dtype('int64')),
        ('IsAudit', dtype('float64')),
        ('TotalRevenue', dtype('int64')),
        ('GrossProfit', dtype('int64')),
        ('OperatingIncomeOrLoss', dtype('int64')),
        ('InterestExpense', dtype('int64')),
        ('IncomeBeforeTax', dtype('int64')),
        ('NetIncome', dtype('int64')),
        ('Capital', dtype('int64')),
        ('Eps', dtype('int64')),
    ]
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime  # noqa
