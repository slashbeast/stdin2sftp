#!/usr/bin/env python

from pathlib import Path

from setuptools import setup


version = '0.1.0'


setup(
    name="stdin2sftp",
    version=version,
    description="stdin to sftp pump",
    long_description=Path('README.rst').read_text(),
    long_description_content_type='text/x-rst',
    author="Piotr Karbowski",
    license="BSD",
    url="https://github.com/slashbeast/stdin2sftp",
    download_url = "https://github.com/slashbeast/stdin2sftp/archive/v{}.tar.gz".format(version),
    install_requires=Path('requirements.txt').read_text().splitlines(),
    package_dir={'stdin2sftp': 'src/stdin2sftp'},
    packages=['stdin2sftp'],
    entry_points={'console_scripts': ['stdin2sftp = stdin2sftp:main']},
)
