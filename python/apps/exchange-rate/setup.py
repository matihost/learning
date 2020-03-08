"""A setuptools based setup module.

Created based on https://github.com/pypa/sampleproject
and dependencies ensured via pipenv-setup sync tooling.
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="exchange_Rate",  # Required
    version="0.0.1",  # Required
    description="A sample Python project showing exchange rate between two currencies",  # Optional
    long_description=long_description,  # Optional
    long_description_content_type="text/markdown",  # Optional (see note above)
    url="https://github.com/matihost/learning",  # Optional
    author="matihost",  # Optional
    classifiers=[  # Optional
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="exchagnerate nbp",  # Optional
    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.5, <4",
    install_requires=[
        "certifi==2019.11.28",
        "chardet==3.0.4",
        "idna==2.9",
        "requests==2.23.0",
        "urllib3==1.25.8",
    ],  # Optional
    dependency_links=[],
    project_urls={"Source": "https://github.com/matihost/learning/",},  # Optional
)