from datetime import datetime

from pytest_aiohutils import file

from fipiran.symbols import (
    Symbol,
    _History,
    index_compare,
    industries,
    search,
    sub_industries,
)

fmelli = Symbol('35425587644337450')


@file('shcarbon_search.json')
async def test_search():
    term = 'کربن'
    instruments, transactions = await search(symbol=term)
    assert len(instruments) == len(transactions)
    assert instruments
    for inst in instruments:
        assert term in inst.smallSymbolName


@file('fmelli_from_name.json')
async def test_symbol_from_name():
    assert (
        f'{await Symbol.from_name("فملی")!r}' == "Symbol('35425587644337450')"
    )


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
    df = await fmelli.history()
    unexpected_cols = (
        set(df.columns.names) == _History.__pydantic_fields__.keys()
    )
    assert not unexpected_cols


@file('symbol_statements.json')
async def test_statements():
    await fmelli.statements()


@file('sub_industries.json')
async def test_sub_industries():
    await sub_industries()


@file('industries.json')
async def test_industries():
    await industries()


@file('index_compare.json')
async def test_index_compare():
    await index_compare()
