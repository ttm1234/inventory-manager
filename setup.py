#!/usr/bin/env python3
from setuptools import setup

import pypandoc


long_description = pypandoc.convert_file('README.md', 'rst')
print('pypandoc -- long_description', type(long_description), long_description)


setup(
    name='inventory-manager',
    version='0.0.9.dev0',
    description='inventory manager, for flash sale inventory. by sqlalchemy and redis.',
    long_description=long_description,
    url='https://github.com/ttm1234/inventory-manager',
    author='ttm1234',
    author_email='',
    # license='Anti 996',
    classifiers=[
        'Intended Audience :: Developers',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        # 'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        # 'Programming Language :: Python :: 3.9',
        # 'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='inventory inventory_manager inventory-manager',
    include_package_data=True,
    packages=[
        'inventory_manager', 'inventory_manager.models',
    ],
    install_requires=["SQLAlchemy", "redis", ],
)

'''
python3 setup.py bdist_wheel
twine upload dist/*
'''
