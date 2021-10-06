from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    readme_file = f.read()

setup(
    name="blkinfo",
    version="0.2.0",
    author="Gennadii Altukhov",
    author_email="grinrag@gmail.com",
    description="blkinfo is a python package to list information about all available or the specified block devices.",
    long_description=readme_file,
    long_description_content_type='text/markdown',
    license="GPLv3",
    url="https://github.com/grinrag/blkinfo",
    packages=['blkinfo'],
    package_dir={"": "src"},
    keywords='lsblk disk blockdevice blockinfo blkinfo iscsi',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
