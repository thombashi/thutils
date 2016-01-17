from __future__ import with_statement
import sys
import setuptools
from setuptools.command.test import test as TestCommand


with open("README.rst") as fp:
    long_description = fp.read()

with open("requirements.txt", "r") as fp:
    requirements = fp.read().splitlines()

major, minor = sys.version_info[:2]

if major == 2 and minor <= 5:
    requirements.extend([
        "argparse",
        "simplejson",
    ])

setuptools.setup(
    name="thutils",
    version="0.1.8",
    author="Tsuyoshi Hombashi",
    author_email="gogogo.vm@gmail.com",
    url="https://github.com/thombashi/thutils",
    description="Personal python utility library",
    long_description=long_description,
    license="GNU Lesser General Public License v3 (LGPLv3)",
    include_package_data=True,
    packages=setuptools.find_packages(exclude=['test*']),
    install_requires=requirements,
    setup_requires=["pytest-runner"],
    tests_require=[
        "pytest",
        "pytest-cov",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    ],
)
