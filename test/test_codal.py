from numpy import dtype
from fipiran.codal import financial_ratios, profit_growth

from test.aiohttp_test_utils import file


@file('financial_ratios.html')
async def test_financial_ratios():
    df = await financial_ratios()
    assert [*df.dtypes.items()] == [
        ('نماد', dtype('O')),
        ('تاریخ انتشار', dtype('O')),
        ('سال', dtype('int64')),
        ('دوره', dtype('int64')),
        ('سال مالی', dtype('O')),
        ('سرمایه', dtype('float64')),
        ('نسبت جاری', dtype('float64')),
        ('حاشیه سود ناخالص', dtype('float64')),
        ('گردش دارایی', dtype('float64')),
        ('نسبت بدهی', dtype('float64')),
        ('ROA', dtype('float64')),
        ('ROE', dtype('float64')),
        ('سودواقعی هر سهم', dtype('int64'))
    ]


@file('profit_growth.html')
async def test_profit_growth():
    df = await profit_growth()
    assert [*df.dtypes.items()] == [
        ('نماد', dtype('O')),
        ('تاریخ انتشار', dtype('O')),
        ('دوره', dtype('O')),
        ('سود واقعی دوره', dtype('O')),
        ('سود واقعی دوره قبل', dtype('O')),
        ('% رشد', dtype('int64'))
    ]
