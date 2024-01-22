from unittest.mock import patch

from aiohutils.tests import file
from jdatetime import datetime as jdatetime
from numpy import dtype
from pandas import DataFrame
from pytest import raises

from fipiran.symbols import Symbol, search


@file('shcarbon.html')
async def test_search():
    symbols = await search('کربن')
    assert symbols == [Symbol('شكربن'), Symbol('شكربنح')]
    assert symbols[0].l30 == 'كربن\u200c ايران\u200c'


def test_symbol_from_name(aiolib):
    assert f'{Symbol("فملی")!r}' == "Symbol('فملی')"


@file('SymbolFMelli.html')
async def test_inscode_cache():
    s = Symbol('فملی')
    assert s._inscode is None
    assert await s.inscode == 35425587644337450
    assert s._inscode == 35425587644337450


@file('priceDataFMelli.html')
async def test_symbol_price_data():
    s = Symbol('فملی', 35425587644337450)
    price_data = await s.price_data()
    assert [*price_data.keys()] == [
        'PriceMin',
        'PriceMax',
        'PDrCotVal',
        'PriceFirst',
        'PClosing',
        'changepdr',
        'changepc',
        'prevPrice',
        'ZTotTran',
        'QTotTran5J',
        'QTotCap',
        'Deven',
        'tmin',
        'tmax',
    ]
    assert type(price_data.pop('Deven')) is jdatetime
    for key in ('changepdr', 'changepc'):
        assert type(price_data.pop(key)) in (int, float)
    assert all(type(v) is int for v in price_data.values())  # noqa: E721


@file('BestLimitDataFMelli.html')
async def test_symbol_best_limit_data():
    d1, d2 = await Symbol('فملی', 35425587644337450).best_limit_data()
    assert type(d1) is type(d2) is DataFrame


@file('RefrenceDataFmelli.html')
async def test_symbol_refrence_data():
    assert await Symbol('فملی', 35425587644337450).reference_data() == {
        'نام نماد': 'فملی',
        'نام شرکت': 'ملی\u200c صنایع\u200c مس\u200c ایران\u200c\u200c',
        'نام صنعت': 'فلزات اساسی',
        'وضعیت': 'مجاز',
        'بازار': 'بورس-بازاراول-تابلو اصلی',
        'حجم مبنا': '8869180',
        'کد معاملاتی نماد': 'IRO1MSMI0001',
    }


@file('statistic30Fmelli.html')
async def test_symbol_statistics():
    assert (
        type(await Symbol('فملی', 35425587644337450).statistic(30))
        is DataFrame
    )


@file('CompanyInfoIndexSarv.html')
async def test_company_info():
    assert await Symbol('سرو', 64942549055019553).company_info() == {
        'نام نماد': 'سرو',
        'نام شرکت': 'سرو سودمند مدبران',
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


@file('HistoryPricePaging_sarv.json')
async def test_price_history():
    ph = await Symbol('سرو').price_history(rows=3)
    data = ph['data']
    assert len(data) == 3
    assert [*data.dtypes.items()] == [
        ('DEven', 'string'),
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
    assert ph['records'] > 500
    assert ph['total'] > 198


@patch('fipiran.symbols._fipiran', side_effect=NotImplementedError)
async def test_price_history_url(get_mock):
    with raises(NotImplementedError):
        # l18 uses persian ی and ک
        await Symbol('دارا یکم').price_history()
    get_mock.assert_called_once_with(  # needs to be called with arabic ي and ك
        'Symbol/HistoryPricePaging?symbolpara=دارا يكم&rows=365&page=1',
        json_resp=True,
    )
