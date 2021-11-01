__version__ = '0.4.0'


from requests import get as _get


_FIPIRAN = 'https://www.fipiran.com/'
_YK = ''.maketrans('يك', 'یک')


def _fipiran(path: str) -> str:
    return _get(f'{_FIPIRAN}{path}').content.decode().translate(_YK)


def search(term) -> list[dict]:
    return _get(_FIPIRAN + 'Home/AutoComplete', data=(('term', term),)).json()
