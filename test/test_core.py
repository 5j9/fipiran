from json import load
from unittest.mock import patch

from pandas import Series
from pandas.testing import assert_series_equal

# noinspection PyProtectedMember
from fipiran import FundProfile, _core, funds, search


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
