from aiohutils.tests import file, patch
from jdatetime import datetime as jdatetime
from numpy import dtype
from pandas import Timestamp
from pytest import raises

from fipiran.data_service import (
    auto_complete_fund,
    auto_complete_index,
    auto_complete_symbol,
    balance_sheet,
    export_index,
    export_symbol,
    financial_ratios,
    profit_loss,
)

string = 'string'


@file('AutoCompleteFundAva.json')
async def test_auto_complete_fund():
    result = await auto_complete_fund('آوا')
    assert type(result) is list
    for record in result:
        assert record.keys() == {'Name', 'RegNo'}
        assert 'آوا' in record['Name']
        assert type(record['RegNo']) is int


@file('AutoCompleteindexHamVazn.json')
async def test_auto_complete_index():
    assert await auto_complete_index('هم وزن') == [
        {'InstrumentID': 'IRX6XTPI0026', 'LVal30': 'شاخص کل (هم وزن)'},
        {'InstrumentID': 'IRXYXTPI0026', 'LVal30': 'شاخص قیمت (هم وزن)'},
        {'InstrumentID': 'IRXZXOCI0026', 'LVal30': 'شاخص کل هم وزن فرابورس'},
    ]


@file('ExportIndexHamVazn.xls.html')
async def test_export_index():
    df = await export_index(
        'شاخص كل (هم وزن)', 14000101, 14000110, 'IRX6XTPI0026'
    )
    assert len(df) == 3
    assert df.iloc[-1].to_list() == [
        'شاخص',
        jdatetime(1400, 1, 7, 0, 0),
        441834.0,
    ]


@patch(
    'fipiran.data_service.auto_complete_index', side_effect=NotImplementedError
)
async def test_export_index_no_instrument_id(mock):
    with raises(NotImplementedError):
        await export_index('هم وزن', 14000101, 15000101)
    mock.assert_called_once_with('هم وزن')


@file('AutoCompleteSymbolMadira.json')
async def test_auto_complete_symbol():
    assert await auto_complete_symbol('كفر') == [
        {'InstrumentID': 'IRO1NASI0001', 'LVal18AFC': 'کفرا'},
        {'InstrumentID': 'IRO7KFRP0001', 'LVal18AFC': 'کفرآور'},
        {'InstrumentID': 'IRR1NASI0101', 'LVal18AFC': 'کفراح'},
        {'InstrumentID': 'IRR7KFRP0101', 'LVal18AFC': 'کفرآورح'},
    ]


@file('ExportSymbolMadira.xls.html')
async def test_export_symbol():
    df = await export_symbol('ماديرا', 14000801, 15000101, 'IRO3IOMZ0001')
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


@patch(
    'fipiran.data_service.auto_complete_symbol',
    side_effect=NotImplementedError,
)
async def test_export_symbol_no_instrument_id(mock):
    with raises(NotImplementedError):
        await export_symbol('ماديرا', 14000801, 15000101)
    mock.assert_called_once_with('ماديرا')


@file('BS_Fmelli_1394.xls')
async def test_balance_sheet():
    df = await balance_sheet('فملی', 1394)
    assert len(df) == 11
    assert [*df.dtypes.items()] == [
        ('Symbol', string),
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
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime


@file('IS_Fmelli_1394.xls')
async def test_profit_loss():
    df = await profit_loss('فملی', 1394)
    assert len(df) == 14
    assert [*df.dtypes.items()] == [
        ('Symbol', string),
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
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime


@file('financial_ratios_fmelli_1394.xls')
async def test_financial_ratios():
    df = await financial_ratios('فملی', 1394)
    assert len(df) == 4
    assert [*df.dtypes.items()] == [
        ('Symbol', string),
        ('PublishDate', dtype('O')),
        ('FinancialYear', dtype('O')),
        ('Year', dtype('int64')),
        ('Priod', dtype('int64')),
        ('CurrentRatio', dtype('float64')),
        ('CashRatio', dtype('float64')),
        ('QuickRatio', dtype('float64')),
        ('DebtRatio', dtype('float64')),
        ('DebtEquityRatio', dtype('float64')),
        ('ROA', dtype('float64')),
        ('ROE', dtype('float64')),
        ('AssetTurnoverRatio', dtype('float64')),
        ('ReceivablesTurnoverRatio', dtype('float64')),
        ('DaySalesInReceivablesTurnoverRatio', dtype('float64')),
        ('InventoryTurnoverRatio', dtype('float64')),
        ('DaySalesInInventoryTurnoverRatio', dtype('float64')),
        ('PayableTurnoverRatio', dtype('float64')),
        ('DaySalesInPayableTurnoverRatio', dtype('float64')),
        ('ProfitMargin', dtype('float64')),
        ('GrossProfitRatio', dtype('float64')),
    ]
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime
