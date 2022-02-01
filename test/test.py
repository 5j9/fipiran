from json import loads
from unittest.mock import patch

from jdatetime import datetime as jdatetime
from numpy import dtype
from pandas import CategoricalDtype, Series, DataFrame, Timestamp
from pandas.testing import assert_series_equal
from pytest import raises

from fipiran.fund import Fund, funds, average_returns
from fipiran.symbol import Symbol, search
from fipiran.data_service import (
    auto_complete_symbol,
    export_symbol,
    mutual_fund_list,
    auto_complete_fund,
    mutual_fund_data,
    auto_complete_index,
    export_index,
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


@patch_get('MutualFundList.xls.html')
def test_mutual_fund_list():
    df = mutual_fund_list()
    assert len(df) == 259
    assert df.columns.to_list() == [
        'RegNo',
        'FundType',
        'Custodian',
        'Guarantor',
        'Manager',
        'Name',
        'WebSite',
    ]


@patch_get('AutoCompleteFundAva.json')
def test_auto_complete_fund():
    assert auto_complete_fund('آوا') == [
        {'RegNo': 11477, 'Name': 'آوای سهام کیان'},
        {'RegNo': 11884, 'Name': 'بازارگردانی آوای زاگرس'},
        {'RegNo': 11729, 'Name': 'قابل معامله آوای معیار'},
        {'RegNo': 11776, 'Name': 'صندوق سرمایه گذاری آوای فردای زاگرس'},
    ]


@patch_get('ExportMFAva.xls.html')
def test_mutual_fund_data():
    df = mutual_fund_data('قابل معامله آوای معیار', '1400/01/01', '1400/12/29', 11729)
    assert df.iloc[-1].to_list() == [
        'قابل معامله آوای معیار',
        jdatetime(1400, 1, 6, 0, 0),
        8373,
        8431,
        8373,
        jdatetime(1399, 5, 6, 0, 0),
        3666009617642,
        437849851,
    ]


@patch('fipiran.data_service.auto_complete_fund', side_effect=NotImplementedError)
def test_mutual_fund_data_no_reg_no(mock):
    with raises(NotImplementedError):
        mutual_fund_data('آوای معیار', '1400/01/01', '1400/12/29')
    mock.assert_called_once_with('آوای معیار')


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


@patch('fipiran.symbol._fipiran', side_effect=NotImplementedError)
def test_price_history_url(get_mock):
    with raises(NotImplementedError):
        # l18 uses persian ی and ک
        Symbol('دارا یکم').price_history()
    get_mock.assert_called_once_with(  # needs to be called with arabic ي and ك
        'Symbol/HistoryPricePaging?symbolpara=دارا يكم&rows=365&page=1', json_resp=True
    )
