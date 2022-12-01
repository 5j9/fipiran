from . import _DataFrame, _fipiran, _read_html


async def financial_ratios() -> _DataFrame:
    text = await _fipiran('Codal/Ratio')
    return _read_html(text)[0]
