"""Setup file for PyPI"""

# To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="eodhd",
    version="1.0.26",
    description="Official EODHD API Python Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://whittle.medium.com",
    author="Michael Whittle",
    author_email="michael@lifecycle-ps.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=["eodhd"]) + ['eodhd.APIs'],
    include_package_data=True,
    install_requires=[
        "websockets>=11.0.3",
        "websocket-client>=1.6.3",
        "requests>=2.31.0",
        "rich>=13.5.2",
        "pandas>=2.1.0",
        "numpy>=1.25.2",
        "matplotlib>=3.7.2",
    ],
    entry_points={
        "console_scripts": [
            "whittlem=eodhd.__main__:main",
        ]
    },
    setup_requires=["pytest-runner==6.0.0"],
    tests_require=["pytest==7.4.2"],
    test_suite="tests",
)
