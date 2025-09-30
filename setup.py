from setuptools import setup, find_packages

setup(
    name="payvo_sdk",
    version="0.0.2",
    author="erruqie",
    author_email="clownl3ss@icloud.com",
    description="Python SDK для работы с Payvo API",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/erruqie/payvo_sdk",
    packages=find_packages(),
    install_requires=[
        "requests>=2.30.0"
    ],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
