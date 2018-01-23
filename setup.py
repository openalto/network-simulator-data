#!/usr/bin/env python3

from os import path, listdir

from setuptools import setup, find_packages


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()


def files(dirname):
    return [path.join(dirname, filename) for filename in listdir(dirname)]


setup(
    name="sfp-eval",
    version="0.1",
    description="Evaluation tools of SFP",
    url="https://github.com/openalto/sfp-eval",
    author="Y.Jace Liu, Jensen Zhang",
    author_email="yang.jace.liu@linux.com, hack@jensen-zhang.site",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Development Status :: 2 - Pre-Alpha",
        "Intented Audience :: Developers",
        "Topic :: System :: Emulators",
    ],
    license="MIT",
    long_description=read("README.md"),
    packages=find_packages(),
    zip_safe=False
)
