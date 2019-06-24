#!/usr/bin/python3
import json
from blkinfo.filters import BlkDiskInfo


def main():

    myblkd = BlkDiskInfo()
    filters = {
        'name': "sd*"
    }

    all_my_disks = myblkd.get_disks(filters)

    json_output = json.dumps(all_my_disks)
    print(json_output)


main()

