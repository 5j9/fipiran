from numpy import dtype
from jdatetime import datetime as jdatetime
from pytest import raises
from pandas import Timestamp

from fipiran.data_service import (
    auto_complete_symbol,
    balance_sheet,
    export_symbol,
    auto_complete_fund,
    auto_complete_index,
    export_index,
    financial_ratios,
    profit_loss,
)
from . import disable_get, patch_get, patch


def setup_module():
    disable_get.start()


def teardown_module():
    disable_get.stop()


@patch_get('AutoCompleteFundAva.json')
def test_auto_complete_fund():
    assert auto_complete_fund('آوا') == [
        {'RegNo': 11477, 'Name': 'آوای سهام کیان'},
        {'RegNo': 11884, 'Name': 'بازارگردانی آوای زاگرس'},
        {'RegNo': 11729, 'Name': 'قابل معامله آوای معیار'},
        {'RegNo': 11776, 'Name': 'صندوق سرمایه گذاری آوای فردای زاگرس'},
    ]


@patch_get('AutoCompleteindexHamVazn.json')
def test_auto_complete_index():
    assert auto_complete_index('هم وزن') == [
        {'LVal30': 'شاخص كل (هم وزن)', 'InstrumentID': 'IRX6XTPI0026'},
        {'LVal30': 'شاخص قيمت (هم وزن)', 'InstrumentID': 'IRXYXTPI0026'},
        {'LVal30': 'شاخص كل هم وزن فرابورس', 'InstrumentID': 'IRXZXOCI0026'},
    ]


@patch_get('ExportIndexHamVazn.xls.html')
def test_export_index():
    df = export_index('شاخص كل (هم وزن)', 14000101, 14000110, 'IRX6XTPI0026')
    assert len(df) == 3
    assert df.iloc[-1].to_list() == ['شاخص', jdatetime(1400, 1, 7, 0, 0), 441834.0]


@patch('fipiran.data_service.auto_complete_index', side_effect=NotImplementedError)
def test_export_index_no_instrument_id(mock):
    with raises(NotImplementedError):
        export_index('هم وزن', 14000101, 15000101)
    mock.assert_called_once_with('هم وزن')


@patch_get('AutoCompleteSymbolMadira.json')
def test_auto_complete_symbol():
    assert auto_complete_symbol('مادیرا') == [
        {'LVal18AFC': 'ماديرا', 'InstrumentID': 'IRO3IOMZ0001'},
        {'LVal18AFC': 'ماديرا', 'InstrumentID': 'IRO7IOMZ0001'},
        {'LVal18AFC': 'ماديراح', 'InstrumentID': 'IRR3IOMZ0101'},
    ]


@patch_get('ExportSymbolMadira.xls.html')
def test_export_symbol():
    df = export_symbol('ماديرا', 14000801, 15000101, 'IRO3IOMZ0001')
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


@patch('fipiran.data_service.auto_complete_symbol', side_effect=NotImplementedError)
def test_export_symbol_no_instrument_id(mock):
    with raises(NotImplementedError):
        export_symbol('ماديرا', 14000801, 15000101)
    mock.assert_called_once_with('ماديرا')


@patch_get('BS_Fmelli_1394.xls')
def test_balance_sheet():
    df = balance_sheet('فملی', 1394)
    assert len(df) == 11
    assert [*df.dtypes.items()] == [
        ('Symbol', dtype('O')),
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
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime  # noqa


@patch_get('IS_Fmelli_1394.xls')
def test_profit_loss():
    df = profit_loss('فملی', 1394)
    assert len(df) == 14
    assert [*df.dtypes.items()] == [
        ('Symbol', dtype('O')),
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
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime  # noqa


@patch_get('financial_ratios_fmelli_1394.xls')
def test_financial_ratios():
    df = financial_ratios('فملی', 1394)
    assert len(df) == 4
    assert [*df.dtypes.items()] == [
        ('Symbol', dtype('O')),
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
    assert type(df.iat[0, 1]) is type(df.iat[0, 2]) is jdatetime  # noqa
