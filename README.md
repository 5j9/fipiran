# fipiran

An async Python library to fetch data from https://www.fipiran.com/.

> [!NOTE]  
> This package is incomplete and still in its initial development phase. The API may change without deprecation.

## Installation

Requires Python 3.13+. Available on [PyPI](https://pypi.org/project/fipiran/).

```bash
$ uv add fipiran
```

## Usage

```python
import asyncio
from fipiran.symbols import Symbol


async def main():
    symbol = await Symbol.from_name('فملی')
    company_info = await symbol.info()
    print(company_info.model_dump_json(indent=2))


asyncio.run(main())
```

There are two main modules:
- `funds`
- `symbols`

Most tabular data functions return a Polars `LazyFrame` for optimized, lazy query evaluations. Use an asyncio-aware REPL, like `python -m asyncio`, to run the code samples below.

### Example 1: Historical Data via Polars LazyFrames

Because `symbol.history()` returns a Polars `LazyFrame`, you append `.collect()` to process or inspect the records eagerly:

```python
>>> from fipiran.symbols import Symbol
>>> symbol = await Symbol.from_name('فملی')
>>> history_lf = await symbol.history(limit=1)
>>> history_lf.collect()
shape: (1, 16)
┌───────────────────┬─────────────────┬──────────────────────┬───┬────────────┬────────────┬────────────┬───────┐
│ insCode           ┆ transactionDate ┆ numberOfTransactions ┆ … ┆ priceFirst ┆ priceYest… ┆ lastStatus ┆ hEven │
│ ---               ┆ ---             ┆ ---                  ┆   ┆ ---        ┆ ---        ┆ ---        ┆ ---   │
│ str               ┆ datetime[μs]    ┆ f64                  ┆   ┆ f64        ┆ f64        ┆ i64        ┆ i64   │
╞═══════════════════╪═════════════════╪══════════════════════╪═══╪════════════╪════════════╪════════════╪═══════╡
│ 35425587644337450 ┆ 2025-10-01      ┆ 11586.0              ┆ … ┆ 6530.0     ┆ 6530.0     ┆ 0          ┆122949 │
└───────────────────┴─────────────────┴──────────────────────┴───┴────────────┴────────────┴────────────┴───────┘
```

### Example 2: Querying Fund Records

Getting a listing of mutual funds as a `LazyFrame`. You can run expressions or filters before calling `.collect()` to grab the final data frame:

```python
>>> from fipiran.funds import funds
>>> lf = await funds()
>>> lf.select(["regNo", "name", "isCompleted"]).limit(5).collect()
shape: (5, 3)
┌───────┬──────────────────────────┬─────────────┐
│ regNo ┆ name                     ┆ isCompleted │
│ ---   ┆ ---                      ┆ ---         │
│ str   ┆ str                      ┆ bool        │
╞═══════╪══════════════════════════╪═════════════╡
│ 11726 ┆ جسورانه فیروزه           ┆ true        │
│ 11603 ┆ جسورانه فناوری بازنشستگی ┆ true        │
│ 11780 ┆ گروه زعفران سحرخیز       ┆ true        │
│ 11772 ┆ طلای سرخ نو ویرا         ┆ true        │
│ 11480 ┆ جسورانه یکم آرمان آتی    ┆ true        │
└───────┴──────────────────────────┴─────────────┘
```

There are many other functions and methods. Please explore the code-base for more info.

If you are interested in other information that is available on fipiran.com but this library has no API for, please [open an issue](https://github.com/5j9/fipiran/issues) for them on GitHub.

## See also

* [5j9/tsetmc](https://github.com/5j9/tsetmc)