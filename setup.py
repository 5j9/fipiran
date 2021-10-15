from setuptools import setup
from os.path import dirname


setup(
    name='fipiran',
    version='0.1.0',
    long_description=open(
        f'{dirname(__file__)}/README.rst', encoding='utf-8').read(),
    long_description_content_type='text/x-rst',
    description='a library to retrieve data from fipiran.com website',
    url='https://github.com/5j9/fipiran',
    author='5j9',
    author_email='5j9@users.noreply.github.com',
    license='GNU General Public License v3 (GPLv3)',
    packages=['fipiran'],
    package_data={'fipiran': ['ids.json']},
    zip_safe=False,
    python_requires='>=3.10',
    install_requires=['requests', 'pandas'],
    tests_require=['pytest'],
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet',
    ],
    keywords='fipiran client')
