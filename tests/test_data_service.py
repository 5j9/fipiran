from datetime import datetime
from operator import itemgetter

from aiohutils.tests import file, patch
from polars import Datetime, Float64, Int64, String, DataFrame
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
    ic = await auto_complete_index('هم وزن')
    df = DataFrame(ic)
    assert df['LVal30'].str.contains('هم وزن').all()
    assert 'IRX6XTPI0026' in df['InstrumentID']


@file('ExportIndexHamVazn.xls.html')
async def test_export_index():
    df = await export_index(
        'شاخص كل (هم وزن)', 14000101, 14000110, 'IRX6XTPI0026'
    )
    assert len(df) == 3
    assert df.row(-1) == (
        'شاخص',
        datetime(2021, 3, 27, 0, 0),
        441834.0,
    )


@patch(
    'fipiran.data_service.auto_complete_index', side_effect=NotImplementedError
)
async def test_export_index_no_instrument_id(mock):
    with raises(NotImplementedError):
        await export_index('هم وزن', 14000101, 15000101)
    mock.assert_called_once_with('هم وزن')


@file('AutoCompleteSymbolMadira.json')
async def test_auto_complete_symbol():
    term = 'كفر'  # contains arabic letters
    ic = await auto_complete_symbol(term)
    df = DataFrame(ic)
    assert set(df.columns) == {'InstrumentID', 'LVal18AFC'}
    # results don't contain arabic letters
    assert df['LVal18AFC'].str.contains('کفر').all()
    assert 'IRO7KFRP0001' in df['InstrumentID']


@file('ExportSymbolMadira.xls.html')
async def test_export_symbol():
    df = await export_symbol('ماديرا', 14000801, 15000101, 'IRO3IOMZ0001')
    # noinspection PyTypeChecker
    assert df.row(-1) == (
        'مادیرا',
        14000801,
        datetime(2021, 10, 23, 0, 0),
        373.0,
        4505128.0,
        32545145672.0,
        7224.0,
        7224.0,
        7224.0,
        7230.0,
        7224.0,
        7604.0,
    )


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
    assert [*zip(df.columns, df.dtypes)] == [
        ('Symbol', String),
        ('PublishDate', Datetime(time_unit='us', time_zone=None)),
        ('FinanceYear', Datetime(time_unit='us', time_zone=None)),
        ('Year', Int64),
        ('period', Int64),
        ('IsAudit', Float64),
        ('cash', Int64),
        ('NetReceivables', Int64),
        ('OtherReceivables', Int64),
        ('ShortTermInvestments', Int64),
        ('Inventory', Int64),
        ('PrePayment', Int64),
        ('TotalCurrentAssets', Int64),
        ('LongTermInvestments', Int64),
        ('PropertyPlantAndEquipment', Int64),
        ('IntangibleAssets', Int64),
        ('TotalAssets', Int64),
        ('AccountsPayable', Int64),
        ('OtherPayable', Int64),
        ('PreRecive', Int64),
        ('TotalCurrentLiabilities', Int64),
        ('TotalLiabilities', Int64),
        ('capital', Int64),
        ('RetainedEarnings', Int64),
        ('TotalStockholderEquity', Int64),
    ]
    assert type(df[0, 1]) is type(df[0, 2]) is datetime


@file('IS_Fmelli_1394.xls')
async def test_profit_loss():
    df = await profit_loss('فملی', 1394)
    assert len(df) == 14
    assert [*zip(df.columns, df.dtypes)] == [
        ('Symbol', String),
        ('publishDate', Datetime(time_unit='us', time_zone=None)),
        ('FinanceYear', Datetime(time_unit='us', time_zone=None)),
        ('Year', Int64),
        ('priod', Int64),
        ('IsAudit', Float64),
        ('TotalRevenue', Int64),
        ('GrossProfit', Int64),
        ('OperatingIncomeOrLoss', Int64),
        ('InterestExpense', Int64),
        ('IncomeBeforeTax', Int64),
        ('NetIncome', Int64),
        ('Capital', Int64),
        ('Eps', Int64),
    ]
    assert type(df[0, 1]) is type(df[0, 2]) is datetime


@file('financial_ratios_fmelli_1394.xls')
async def test_financial_ratios():
    df = await financial_ratios('فملی', 1394)
    assert len(df) == 4
    assert [*zip(df.columns, df.dtypes)] == [
        ('Symbol', String),
        ('PublishDate', Datetime(time_unit='us', time_zone=None)),
        ('FinancialYear', Datetime(time_unit='us', time_zone=None)),
        ('Year', Int64),
        ('Priod', Int64),
        ('CurrentRatio', Float64),
        ('CashRatio', Float64),
        ('QuickRatio', Float64),
        ('DebtRatio', Float64),
        ('DebtEquityRatio', Float64),
        ('ROA', Float64),
        ('ROE', Float64),
        ('AssetTurnoverRatio', Float64),
        ('ReceivablesTurnoverRatio', Float64),
        ('DaySalesInReceivablesTurnoverRatio', Float64),
        ('InventoryTurnoverRatio', Float64),
        ('DaySalesInInventoryTurnoverRatio', Float64),
        ('PayableTurnoverRatio', Float64),
        ('DaySalesInPayableTurnoverRatio', Float64),
        ('ProfitMargin', Float64),
        ('GrossProfitRatio', Float64),
    ]
    assert type(df[0, 1]) is type(df[0, 2]) is datetime
