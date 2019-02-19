from setuptools import setup


setup(
    name="blkinfo",
    version="0.0.2",
    author="Gennadii Altukhov",
    author_email="galt@redhat.com",
    description="Library for listing all block devices available in the system using additional filters",
    license="GPLv3",
    url="https://github.com/grinrag/disk_enumeration_poc",
    packages=['blkinfo'],
    package_dir={"": "src"},
    keywords='lsblk disk blockdevice blockinfo blkinfo',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
)
