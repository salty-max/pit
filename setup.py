from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="pit",
    version="0.1.0",
    author="salty-max",
    author_email="max@jellycat.fr",
    description="A cheap git clone in Python3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/salty-max/pit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
