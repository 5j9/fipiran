Note: This is package is incomplete and still in initial development phase. The API may change without deprecation.

Installation
------------
Requires Python 3.10+.

.. code-block:: bash

    $ pip install fipiran

Usage
-----

For any async operation ``fipiran.SESSION`` needs to be set to an aiohttp.ClientSession instance:

.. code-block:: python

    import tsetmc
    import aiohttp

    async def main():
        async with aiohttp.ClientSession() as tsetmc.SESSION:
            ...

``fipiran.Session()`` provides a shorter alternative for the above:

.. code-block:: python

    import fipiran

    async def main():
        async with fipiran.Session():
            ...

There are three modules:

- data_service
- funds
- symbols

Example 1:

.. code-block:: python

    import fipiran
    from fipiran.symbols import Symbol

    async with fipiran.Session():
        d = await Symbol('فملی').company_info()

    # d:
    {'نام نماد': 'فملی',
     'نام شرکت': 'ملی صنایع مس ایران',
     'مدیر عامل': 'اردشیر سعدمحمدی',
     'تلفن': '021-88724410',
     'فکس': '021-88729014',
     'آدرس': 'مجتمع مس سرچشمه و مجتمع مس میدوک در استان کرمان و مجتمع مس سونگون در تبریز شهرستان ورزقان واقع شده اند.',
     'وب سایت': 'www.nicico.com',
     'ایمیل': 'office@nicico.com',
     'سال مالی': '12/29',
     'موضوع فعالیت': 'اکتشافات،  استخراج و  بهره برداری از معادن  مس  ایران'}

Example 2:

Getting list of funds as a pandas DataFrame object:

.. code-block:: python

    >>> from fipiran.funds import funds
    >>> async with fipiran.Session():
            f  = await funds()
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
