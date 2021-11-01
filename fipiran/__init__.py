__version__ = '0.3.1.dev0'


from requests import get as _get


_FIPIRAN = 'https://www.fipiran.com/'


def search(term) -> list[dict]:
    return _get(_FIPIRAN + 'Home/AutoComplete', data=(('term', term),)).json()
