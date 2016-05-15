from __future__ import with_statement
import os.path
import sys
import setuptools


MISC_DIR = "misc"
REQUIREMENT_DIR = "requirements"


with open("README.rst") as fp:
    long_description = fp.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    install_requires = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    tests_require = [line.strip() for line in f if line.strip()]


major, minor = sys.version_info[:2]
if major == 2 and minor <= 5:
    install_requires.extend([
        "argparse",
        "simplejson",
    ])

setuptools.setup(
    name="thutils",
    version="0.1.23",
    author="Tsuyoshi Hombashi",
    author_email="gogogo.vm@gmail.com",
    url="https://github.com/thombashi/thutils",
    description="Personal python utility library",
    long_description=long_description,
    license="GNU Lesser General Public License v3 (LGPLv3)",
    include_package_data=True,
    packages=setuptools.find_packages(exclude=['test*']),
    install_requires=install_requires,
    setup_requires=["pytest-runner"],
    tests_require=tests_require,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
