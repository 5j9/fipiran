An async python library to fetch data from https://www.fipiran.com/ .

Note: This is package is incomplete and still in initial development phase. The API may change without deprecation.

Installation
------------
Requires Python 3.13+.

.. code-block:: bash

    $ pip install fipiran

Usage
-----

.. code-block:: python

    import asyncio

    from fipiran.symbols import Symbol


    async def main():
        symbol = await Symbol.from_name('فملی')
        company_info = await symbol.info()
        print(company_info.model_dump_json(indent=2))


    asyncio.run(main())

There are two main modules:

- funds
- symbols

Use an asyncio-aware REPL, like ``python -m asyncio``, to run the code samples below.

Example 1:

.. code-block:: python

    >>> from fipiran.symbols import Symbol
    >>> symbol = await Symbol.from_name('فملی')
    >>> history = await symbol.history(limit=1)
    >>> for entry in history:
            print(entry.model_dump_json(indent=2))
    {
    "insCode": "35425587644337450",
    "transactionDate": "2025-10-01T00:00:00",
    "numberOfTransactions": 11586.0,
    "numberOfVolume": 575913522.0,
    "transactionValue": 3847273607390.0,
    "closingPrice": 6680.0,
    "adjPriceForward": 7554.014596889284,
    "adjPriceBackward": 7554.0145968,
    "lastTransaction": 6720.0,
    "changePrice": 190.0,
    "priceMin": 6410.0,
    "priceMax": 6720.0,
    "priceFirst": 6530.0,
    "priceYesterday": 6530.0,
    "lastStatus": 0,
    "hEven": 122949
    }

Example 2:

Getting list of funds as a pandas DataFrame object.

.. code-block:: python

    >>> from fipiran.funds import funds
    >>> await funds()
         regNo                                  name  ...      isCompleted  fundWatch
    0    11726                        جسورانه فیروزه  ...         True       None
    1    11603              جسورانه فناوری بازنشستگی  ...         True       None
    2    11780                    گروه زعفران سحرخیز  ...         True       None
    3    11772                      طلای سرخ نو ویرا  ...         True       None
    4    11480                 جسورانه یکم آرمان آتی  ...         True       None
    ..     ...                                   ...  ...          ...        ...
    308  11916                    با درآمد ثابت آریا  ...        False       None
    309  11922                      آوای تاراز زاگرس  ...        False       None
    310  11927                    صندوق در صندوق صنم  ...        False       None
    311  11931  اختصاصی بازارگردانی توسعه سهام عدالت  ...        False       None
    312  11933       اختصاصی بازارگردانی تثبیت پاداش  ...        False       None
    [313 rows x 37 columns]

There are many other functions and methods. Please explore the code-base for more info.

If you are interested in other information that are available on fipiran.com but this library has no API for, please `open an issue`_ for them on github.

See also
--------

* https://github.com/5j9/tsetmc


.. _open an issue: https://github.com/5j9/fipiran/issues
