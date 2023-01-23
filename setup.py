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
    version="1.0.8",
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
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(include=["eodhd"]),
    include_package_data=True,
    install_requires=[
        "websockets==10.3",
        "websocket-client==1.3.3",
        "requests==2.28.1",
        "rich==12.5.1",
        "pandas==1.3.5",
        "numpy==1.21.6",
    ],
    entry_points={
        "console_scripts": [
            "whittlem=eodhd.__main__:main",
        ]
    },
    setup_requires=["pytest-runner==6.0.0"],
    tests_require=["pytest==7.1.2"],
    test_suite="tests",
)
