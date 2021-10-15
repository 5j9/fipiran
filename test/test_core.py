from datetime import datetime
from json import load
from unittest.mock import patch

from pandas import DataFrame, DatetimeIndex, Series
from pandas.testing import assert_frame_equal, assert_series_equal
from numpy import dtype
from pytest import raises

from fipiran import FundProfile, _core


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
    assert df.index.dtype == dtype('<M8[ns]')


@patch_api('getfundnetassetchart_atlas')
def test_nav_history():
    df = fp.nav_history()
    assert_series_equal(df.dtypes, Series(['int64'], ['netAsset']))
    assert len(df) == 366
    assert df.index.dtype == dtype('<M8[ns]')


@patch_api('getfund_atlas')
def test_info():
    info = fp.info()
    assert len(info) == 54
    assert type(info) is dict
