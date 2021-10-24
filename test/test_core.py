from json import load
from unittest.mock import patch

from pandas import Series
from pandas.testing import assert_series_equal

# noinspection PyProtectedMember
from fipiran import FundProfile, _core, funds, search, Symbol
# noinspection PyProtectedMember
from fipiran._core import YK, jdatetime, DataFrame

disable_api = patch.object(_core, 'api', side_effect=RuntimeError(
    'api should not be called during tests'))


def setup_module():
    disable_api.start()


def teardown_module():
    disable_api.stop()


def patch_api(name):
    with open(f'{__file__}/../testdata/{name}.json', 'rb') as f:
        j = load(f)
    return patch.object(_core, 'api', lambda _: j)


def patch_fipiran(name):
    with open(f'{__file__}/../testdata/{name}.html', 'r', encoding='utf8') as f:
        text = f.read()
    return patch.object(_core, 'fipiran', lambda _: text.translate(YK))


fp = FundProfile(11215)


def test_repr():
    assert repr(fp) == 'FundProfile(11215)'
    assert repr(FundProfile('11215')) == "FundProfile('11215')"


@patch_api('getfundchartasset_atlas')
def test_asset_allocation():
    d = fp.asset_allocation()
    del d['fiveBest']
    assert sum(d.values()) == 100


@patch_api('getfundchart_atlas')
def test_issue_cancel_history():
    df = fp.issue_cancel_history()
    assert_series_equal(df.dtypes, Series(['float64', 'float64'], ['issueNav', 'cancelNav']))
    assert len(df) == 366
    assert df.index.dtype == '<M8[ns]'


@patch_api('getfundnetassetchart_atlas')
def test_nav_history():
    df = fp.nav_history()
    assert_series_equal(df.dtypes, Series(['int64'], ['netAsset']))
    assert len(df) == 366
    assert df.index.dtype == '<M8[ns]'


@patch_api('getfund_atlas')
def test_info():
    info = fp.info()
    assert len(info) == 54
    assert type(info) is dict


@patch_api('fundlist')
def test_funds():
    df = funds()
    assert len(df) == 272


@patch_api('autocomplete_arzesh')
def test_search():
    assert search('ارزش') == [
        {'LVal18AFC': 'وآفر', 'LSoc30': ' سرمايه گذاري ارزش آفرينان'},
        {'LVal18AFC': 'وارزش', 'LSoc30': 'ارزش آفرينان پاسارگاد'},
        {'LVal18AFC': 'وآفر', 'LSoc30': 'سرمايه گذاري ارزش آفرينان'},
        {'LVal18AFC': 'ارزش', 'LSoc30': 'صندوق س ارزش آفرين بيدار-سهام'},
        {'LVal18AFC': 'ومدير', 'LSoc30': 'گ.مديريت ارزش سرمايه ص ب كشوري'}]


def test_symbol_from_name():
    assert f'{Symbol("فملی")!r}' == "Symbol('فملی')"


@patch_fipiran('SymbolFMelli')
def test_inscode_cache():
    s = Symbol("فملی")
    assert s._inscode is None
    assert s.inscode == 35425587644337450
    assert s._inscode is not None


@patch_fipiran('priceDataFMelli')
def test_symbol_price_data():
    s = Symbol('فملی', 35425587644337450)
    assert s.price_data() == {
        'PriceMin': 13140.0, 'PriceMax': 13770.0, 'PDrCotVal': 13290.0,
        'PriceFirst': 13770.0, 'PClosing': 13300.0, 'changepdr': -1.77,
        'changepc': -1.7, 'prevPrice': 13530.0, 'ZTotTran': 10103.0,
        'QTotTran5J': 71934487.0, 'QTotCap': 956433812420.0,
        'Deven': jdatetime(1400, 8, 1, 12, 30), 'tmin': 12860.0, 'tmax': 14200.0}


@patch_fipiran('BestLimitDataFMelli')
def test_symbol_best_limit_data():
    d1, d2 = Symbol('فملی', 35425587644337450).best_limit_data()
    assert type(d1) is type(d2) is DataFrame


@patch_fipiran('RefrenceDataFmelli')
def test_symbol_refrence_data():
    assert Symbol('فملی', 35425587644337450).refrence_data() == {
        'نام نماد': 'فملی',
        'نام شرکت': 'ملی\u200c صنایع\u200c مس\u200c ایران\u200c\u200c',
        'نام صنعت': 'فلزات اساسی', 'وضعیت': 'مجاز',
        'بازار': 'بورس-بازاراول-تابلو اصلی',
        'حجم مبنا': '8869180', 'کد معاملاتی نماد': 'IRO1MSMI0001'}


@patch_fipiran('statistic30Fmelli')
def test_symbol_refrence_data():
    assert type(Symbol('فملی', 35425587644337450).statistic(30)) is DataFrame


@patch_fipiran('CompanyInfoIndexSarv')
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