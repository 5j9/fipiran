from aiohutils.tests import file
from polars import Float64, Int64, String

from fipiran.codal import financial_ratios, profit_decline, profit_growth


@file('financial_ratios.html')
async def test_financial_ratios():
    df = await financial_ratios()
    assert [*zip(df.columns, df.dtypes)] == [
        ('نماد', String),
        ('تاریخ انتشار', String),
        ('سال', Int64),
        ('دوره', Int64),
        ('سال مالی', String),
        ('سرمایه', Float64),
        ('نسبت جاری', Float64),
        ('حاشیه سود ناخالص', Float64),
        ('گردش دارایی', Float64),
        ('نسبت بدهی', Float64),
        ('ROA', Float64),
        ('ROE', Float64),
        ('سودواقعی هر سهم', Int64),
    ]


@file('profit_growth.html')
async def test_profit_growth():
    df = await profit_growth()
    assert [*zip(df.columns, df.dtypes)] == [
        ('نماد', String),
        ('تاریخ انتشار', String),
        ('دوره', String),
        ('سود واقعی دوره', Int64),
        ('سود واقعی دوره قبل', Int64),
        ('% رشد', Int64),
    ]


@file('profit_decline.html')
async def test_profit_decline():
    df = await profit_decline()
    assert [*zip(df.columns, df.dtypes)] == [
        ('نماد', String),
        ('تاریخ انتشار', String),
        ('دوره', String),
        ('سود واقعی دوره', Int64),
        ('سود واقعی دوره قبل', Int64),
        ('% رشد', Int64),
    ]
