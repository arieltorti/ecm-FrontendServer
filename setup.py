# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

version = "1.1.0"


setup(
    name="ecm",
    url="https://github.com/tutuca/potaje",
    author="fudepan",
    author_email="daniel@fudepan.org.ar",
    version=version,
    package_data={"dist": ["*"], "templates": ["*.html"]},
    packages=find_packages(),
    install_requires=[
        "flask",
        "pandas",
        "scipy",
        "matplotlib",
        "gunicorn",
        "sqlalchemy",
        "flask-sqlalchemy",
        "pydantic",
        "sympy",
    ],
)
