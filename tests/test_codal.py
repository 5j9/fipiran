from aiohutils.tests import file
from numpy import dtype

from fipiran.codal import financial_ratios, profit_decline, profit_growth

string = 'string'


@file('financial_ratios.html')
async def test_financial_ratios():
    df = await financial_ratios()
    assert [*df.dtypes.items()] == [
        ('نماد', string),
        ('تاریخ انتشار', string),
        ('سال', dtype('int64')),
        ('دوره', dtype('int64')),
        ('سال مالی', string),
        ('سرمایه', dtype('float64')),
        ('نسبت جاری', dtype('float64')),
        ('حاشیه سود ناخالص', dtype('float64')),
        ('گردش دارایی', dtype('float64')),
        ('نسبت بدهی', dtype('float64')),
        ('ROA', dtype('float64')),
        ('ROE', dtype('float64')),
        ('سودواقعی هر سهم', dtype('int64')),
    ]


@file('profit_growth.html')
async def test_profit_growth():
    df = await profit_growth()
    assert [*df.dtypes.items()] == [
        ('نماد', string),
        ('تاریخ انتشار', string),
        ('دوره', string),
        ('سود واقعی دوره', dtype('int64')),
        ('سود واقعی دوره قبل', dtype('int64')),
        ('% رشد', dtype('int64')),
    ]


@file('profit_decline.html')
async def test_profit_decline():
    df = await profit_decline()
    assert [*df.dtypes.items()] == [
        ('نماد', string),
        ('تاریخ انتشار', string),
        ('دوره', string),
        ('سود واقعی دوره', dtype('int64')),
        ('سود واقعی دوره قبل', dtype('int64')),
        ('% رشد', dtype('int64')),
    ]
