from setuptools import setup, find_packages

setup(
    name="ewelink-pylib",
    version="0.1.0",
    description="A reusable Python client library and CLI utility for eWeLink V2 API",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    author="Your Name",
    url="https://github.com/yourusername/ewelink-pylib",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "ewelink=ewelink.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
