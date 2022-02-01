from unittest.mock import patch

from jdatetime import datetime as jdatetime
from numpy import dtype
from pandas import CategoricalDtype, DataFrame
from pytest import raises

from fipiran.symbols import Symbol, search
from . import disable_get, patch_get


def setup_module():
    disable_get.start()


def teardown_module():
    disable_get.stop()


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
