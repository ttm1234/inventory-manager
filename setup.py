#!/usr/bin/env python3
from setuptools import setup

setup(
    name='inventory-manager',
    version='0.0.6.dev',
    description='inventory manager, for flash sale inventory. by sqlalchemy and redis.',
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
    packages=[
        'inventory_manager', 'inventory_manager.models',
    ],
    install_requires=["SQLAlchemy", "redis", ],
    include_package_data=True,
)


'''
python3 setup.py bdist_wheel
twine upload dist/*
'''
