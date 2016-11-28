# import multiprocessing to avoid this bug (http://bugs.python.org/issue15881#msg170215)
import multiprocessing
assert multiprocessing
import re
from setuptools import setup, find_packages


def get_version():
    """
    Extracts the version number from the version.py file.
    """
    VERSION_FILE = 'data_schema/version.py'
    mo = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', open(VERSION_FILE, 'rt').read(), re.M)
    if mo:
        return mo.group(1)
    else:
        raise RuntimeError('Unable to find version string in {0}.'.format(VERSION_FILE))


setup(
    name='django-data-schema',
    version=get_version(),
    description='Schemas over dictionaries and models in Django',
    long_description=open('README.md').read(),
    url='https://github.com/ambitioninc/django-data-schema',
    author='Wes Kendall',
    author_email='opensource@ambition.com',
    keywords='Django Data Schema',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
    ],
    license='MIT',
    install_requires=[
        'django>=1.8',
        'django-manager-utils>=0.12.0',
        'fleming>=0.4.4',
        'python-dateutil>=2.2',
    ],
    tests_require=[
        'django-dynamic-fixture',
        'psycopg2',
        'django-nose',
        'mock',
    ],
    test_suite='run_tests.run_tests',
    include_package_data=True,
)
