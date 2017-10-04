"""
django-krowa
"""
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test

#def run_tests(*args):
    #from krowa.tests import run_tests
    #errors = run_tests()
    #if errors:
        #sys.exit(1)
    #else:
        #sys.exit(0)

#test.run_tests = run_tests

setup(
    name="django-krowa",
    version="0.0.1",
    packages=['krowa'],
    license="The MIT License (MIT)",
    include_package_data = True,
    description=("A sequence search tool."),
    long_description=("A sequence search tool "
                "https://github.com/rlalik/TypeWriter"),
    author="Rafal Lalik",
    author_email="rafallalik@gmail.com",
    maintainer="Rafal Lalik",
    maintainer_email="rafallalik@gmail.com",
    url="https://github.com/rlalik/django-krowa/",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Framework :: Django',
    ],
    test_suite="dummy",
)
