"""Setup for packages
"""

from io import open
from os import path
from setuptools import find_packages, setup

from flask_restplus_sqlalchemy import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    required = f.read().splitlines()
with open(path.join(here, 'requirements-dev.txt')) as f:
    required_dev = f.read().splitlines()


setup(
    name='flask_restplus_sqlalchemy',
    version=__version__,
    description='Flask RestPlus SqlAlchemy',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://bluemner.github.io/flask_restplus_sqlalchemy/',
    author='Brandon Bluemner',
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Framework :: Flask',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    keywords='flask restplus api sql SqlAlchemy swagger models',
    packages=find_packages(),
    python_requires='>=3.5',
    install_requires=required,
    extras_require={
        'dev': required_dev,
        'test': required_dev,
    },

    project_urls={
        'Bug Reports': 'https://github.com/bluemner/flask_restplus_sqlalchemy/issues',
        'Source': 'https://github.com/bluemner/flask_restplus_sqlalchemy',
    },
)
