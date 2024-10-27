# backend/redis_service/setup.py
from setuptools import setup, find_packages

setup(
    name="redis_service",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "redis>=4.0.0",
        "aioredis>=2.0.0",
    ],
)