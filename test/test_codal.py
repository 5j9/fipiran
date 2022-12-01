from numpy import dtype
from fipiran.codal import financial_ratios

from test.aiohttp_test_utils import file


@file('financial_ratios.json')
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
