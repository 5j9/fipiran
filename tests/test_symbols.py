from datetime import datetime

import polars as pl
from pytest_aiohutils import file

from fipiran.symbols import (
    HistoryItem,
    Symbol,
    index_compare,
    industries,
    search,
    sub_industries,
)

fmelli = Symbol('35425587644337450')


@file('shcarbon_search.json')
async def test_search():
    term = 'کربن'
    instruments_lf, transactions_lf = await search(symbol=term)

    assert isinstance(instruments_lf, pl.LazyFrame)
    assert isinstance(transactions_lf, pl.LazyFrame)

    # Check total lengths lazily
    inst_count = instruments_lf.select(pl.len()).collect().item()
    tx_count = transactions_lf.select(pl.len()).collect().item()

    assert inst_count >= tx_count
    assert inst_count > 0

    # Assert all returned instruments contain the term using native Polars expressions
    matched_count = (
        instruments_lf.filter(pl.col('smallSymbolName').str.contains(term))
        .select(pl.len())
        .collect()
        .item()
    )
    assert matched_count == inst_count


@file('fmelli_from_name.json')
async def test_symbol_from_name():
    sym = await Symbol.from_name('فملی')
    assert repr(sym) == "Symbol('35425587644337450')"


@file('symbol_info.json')
async def test_info():
    await fmelli.info()


@file('symbol_statistics.json')
async def test_statistics():
    await fmelli.statistics(date=datetime.today())


@file('symbol_efficiency.json')
async def test_efficiency():
    await fmelli.efficiency(date=datetime.today())


@file('symbol_publisher.json')
async def test_publisher():
    await fmelli.publisher()


@file('symbol_history.json')
async def test_history():
    lf = await fmelli.history()
    assert isinstance(lf, pl.LazyFrame)

    # Check against HistoryItem fields (the rows inside the list)
    columns = set(lf.collect_schema().names())
    unexpected_cols = columns - HistoryItem.__pydantic_fields__.keys()
    assert not unexpected_cols


@file('symbol_statements.json')
async def test_statements():
    await fmelli.statements()


@file('sub_industries.json')
async def test_sub_industries():
    lf = await sub_industries()
    assert isinstance(lf, pl.LazyFrame)
    assert lf.select(pl.len()).collect().item() > 0


@file('industries.json')
async def test_industries():
    lf = await industries()
    assert isinstance(lf, pl.LazyFrame)
    assert lf.select(pl.len()).collect().item() > 0


@file('index_compare.json')
async def test_index_compare():
    lf = await index_compare()
    assert isinstance(lf, pl.LazyFrame)
    assert lf.select(pl.len()).collect().item() > 0
