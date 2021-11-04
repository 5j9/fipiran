from json import loads
from unittest.mock import patch

from jdatetime import datetime as jdatetime
from pandas import Series, DataFrame, NA
from pandas.testing import assert_series_equal

from fipiran.fund import FundProfile, funds, average_returns, ratings
from fipiran.symbol import Symbol
from fipiran import search
from fipiran.data_service import mutual_fund_list, auto_complete_fund, \
    mutual_fund_data


disable_get = patch('fipiran._get', side_effect=RuntimeError(
    '_get should not be called during tests'))


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


fp = FundProfile(11215)


def test_repr():
    assert repr(fp) == 'FundProfile(11215)'
    assert repr(FundProfile('11215')) == "FundProfile('11215')"


@patch_get('getfundchartasset_atlas.json')
def test_asset_allocation():
    d = fp.asset_allocation()
    del d['fiveBest']
    assert sum(d.values()) == 100


@patch_get('getfundchart_atlas.json')
def test_issue_cancel_history():
    df = fp.issue_cancel_history()
    assert_series_equal(df.dtypes, Series(['float64', 'float64'], ['issueNav', 'cancelNav']))
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


@patch_get('fundlist.json')
def test_funds():
    df = funds()
    assert len(df) == 272


@patch_get('autocomplete_arzesh.html')
def test_search():
    assert search('ارزش') == [
        {'LVal18AFC': 'وآفر', 'LSoc30': ' سرمايه گذاري ارزش آفرينان'},
        {'LVal18AFC': 'وارزش', 'LSoc30': 'ارزش آفرينان پاسارگاد'},
        {'LVal18AFC': 'وآفر', 'LSoc30': 'سرمايه گذاري ارزش آفرينان'},
        {'LVal18AFC': 'ارزش', 'LSoc30': 'صندوق س ارزش آفرين بيدار-سهام'},
        {'LVal18AFC': 'ومدير', 'LSoc30': 'گ.مديريت ارزش سرمايه ص ب كشوري'}]


def test_symbol_from_name():
    assert f'{Symbol("فملی")!r}' == "Symbol('فملی')"


@patch_get('SymbolFMelli.html')
def test_inscode_cache():
    s = Symbol("فملی")
    assert s._inscode is None
    assert s.inscode == 35425587644337450
    assert s._inscode is not None


@patch_get('priceDataFMelli.html')
def test_symbol_price_data():
    s = Symbol('فملی', 35425587644337450)
    assert s.price_data() == {
        'PriceMin': 13140.0, 'PriceMax': 13770.0, 'PDrCotVal': 13290.0,
        'PriceFirst': 13770.0, 'PClosing': 13300.0, 'changepdr': -1.77,
        'changepc': -1.7, 'prevPrice': 13530.0, 'ZTotTran': 10103.0,
        'QTotTran5J': 71934487.0, 'QTotCap': 956433812420.0,
        'Deven': jdatetime(1400, 8, 1, 12, 30), 'tmin': 12860.0, 'tmax': 14200.0}


@patch_get('BestLimitDataFMelli.html')
def test_symbol_best_limit_data():
    d1, d2 = Symbol('فملی', 35425587644337450).best_limit_data()
    assert type(d1) is type(d2) is DataFrame


@patch_get('RefrenceDataFmelli.html')
def test_symbol_refrence_data():
    assert Symbol('فملی', 35425587644337450).refrence_data() == {
        'نام نماد': 'فملی',
        'نام شرکت': 'ملی\u200c صنایع\u200c مس\u200c ایران\u200c\u200c',
        'نام صنعت': 'فلزات اساسی', 'وضعیت': 'مجاز',
        'بازار': 'بورس-بازاراول-تابلو اصلی',
        'حجم مبنا': '8869180', 'کد معاملاتی نماد': 'IRO1MSMI0001'}


@patch_get('statistic30Fmelli.html')
def test_symbol_refrence_data():
    assert type(Symbol('فملی', 35425587644337450).statistic(30)) is DataFrame


@patch_get('CompanyInfoIndexSarv.html')
def test_company_info():
    assert Symbol('سرو', 64942549055019553).company_info() == {
        'نام نماد': 'سرو',
        'نام شرکت': 'صندوق سرمایه گذاری سرو سودمند مدبران',
        'مدیر عامل': 'رضا درخشان فر', 'تلفن': '021-26231274',
        'فکس': '', 'آدرس': '', 'وب سایت': '', 'ایمیل': '',
        'سال مالی': '09/30',
        'موضوع فعالیت': (
            'موضوع فعالیت صندوق، سرمایه\u200cگذاری در انواع اوراق'
            ' بهادار از جمله سهام و حق تقدم'
            ' سهام پذیرفته¬شده در بورس تهران و '
            'فرابورس ایران، گواهی سپرده کالایی،'
            ' اوراق بهادار با درآمد ثابت، سپرده\u200cها و گواهی¬های'
            ' سپردۀ بانکی است.')}


@patch_get('MFBazdehAVG.html')
def test_average_returns():
    df = average_returns()
    assert type(df) is DataFrame
    assert len(df) == 4
    assert df.query('`نوع صندوق` == "در سهام"')['میانگین بازدهی سال(%)'][0] == 28.4


@patch_get('Rating.html')
def test_ratings():
    df = ratings()
    assert len(df) == 258
    assert df.columns.to_list() == [
        'نام صندوق', 'عملکرد 1 ساله', 'عملکرد 3 ساله', 'عملکرد 5 ساله',
        'تاریخ بروزرسانی']
    assert all(t == float for t in df.dtypes[1:4])
    assert type(df.iat[1, -1]) is jdatetime
    assert df.iat[0, -1] is NA


@patch_get('MutualFundList.xls.html')
def test_mutual_fund_list():
    df = mutual_fund_list()
    assert len(df) == 259
    assert df.columns.to_list() == [
        'RegNo', 'FundType', 'Custodian', 'Guarantor', 'Manager', 'Name',
        'WebSite']


@patch_get('AutoCompleteFundAva.json')
def test_auto_complete_fund():
    assert auto_complete_fund('آوا') == [
        {'RegNo': 11477, 'Name': 'آوای سهام کیان'},
        {'RegNo': 11884, 'Name': 'بازارگردانی آوای زاگرس'},
        {'RegNo': 11729, 'Name': 'قابل معامله آوای معیار'},
        {'RegNo': 11776, 'Name': 'صندوق سرمایه گذاری آوای فردای زاگرس'}]


@patch_get('ExportMFAva.xls.html')
def test_mutual_fund_data():
    df = mutual_fund_data(
        'قابل معامله آوای معیار', 11729, '1400/01/01', '1400/12/29')
    assert df.iloc[0].to_list() == [
        'قابل معامله آوای معیار',
        jdatetime(1400, 8, 10, 0, 0), 7835, 7886, 7835,
        jdatetime(1399, 5, 6, 0, 0), 848853125486, 108349851]
