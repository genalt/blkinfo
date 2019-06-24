"""blkinfo is a python library to list information about all available or the specified block devices.
It bases on lsblk command line tool, provided by util-linux, in addition, it collects information about block devices,
using /sys/block, /sys/devices, /proc directories.
"""

from .filters import BlkDiskInfo
