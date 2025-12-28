"""Setup file for PyPI"""

from os import path
from setuptools import setup, find_packages

HERE = path.abspath(path.dirname(__file__))

with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="eodhd",
    version="1.3.2",
    description="Official EODHD API Python Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://eodhd.com",
    author="Michael Whittle, Alex Chernyshev",
    author_email="support@eodhistoricaldata.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    packages=find_packages(exclude=("tests", "tests.*")),
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
    entry_points={"console_scripts": ["eodhd=eodhd.__main__:main"]}

)
