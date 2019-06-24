"""This module contains BlkDiskInfo class which implement filtering for
block devices in a system
"""

import glob
import re

from .wrappers import LsBlkWrapper, DISK_TYPES, ADDITIONAL_DISK_FILTER, SYS_BLOCK


class BlkDiskInfo(LsBlkWrapper):
    """ BlkDeviceInfo is a class to provide basic information about
        disks available in the system and different parameters related to block devices
    """

    def get_disks(self, filters=None):
        """method returns all disks available in the system, after applying filters"""

        result = []
        if not self._disks:
            return result

        if not filters:
            filters = []

        blacklist = set()

        # preprocess multipath and raid devices
        for dn in self._disks:
            if self._disks[dn]['type'] == 'mpath':
                for p in self._disks[dn]['parents']:
                    # show only multipath disk itself, ignore parents
                    blacklist.add(p)
            elif self._disks[dn]['type'].startswith('raid'):

                # if raid is assembled with parents w/o partitions
                # we should show only raid and ignore all parents
                ignore_parents = True

                for p in self._disks[dn]['parents']:
                    if len(self._disks[p]['children']) != 1:
                        ignore_parents = False
                        break

                if ignore_parents:
                    for p in self._disks[dn]['parents']:
                        blacklist.add(p)

        raids = set()
        mpaths = set()

        # iterate through all disks in the system
        for dn in self._disks:
            disk = self._disks[dn]
            if (disk['type'] not in DISK_TYPES) and (not disk['type'].startswith('raid')) or dn in blacklist:
                continue

            if disk['type'].startswith('raid'):
                if disk['name'] not in raids:
                    raids.add(disk['name'])
                else:
                    continue

            if disk['type'] == 'mpath':
                if disk['name'] not in mpaths:
                    mpaths.add(disk['name'])
                else:
                    continue

            all_filters_passed = True

            for f_name in filters:
                if not all_filters_passed:
                    break

                # take into account only filter we can apply
                if f_name in ADDITIONAL_DISK_FILTER or f_name in disk:

                    if f_name == 'min_size':
                        if int(disk['size']) < filters['min_size']:
                            all_filters_passed = False
                    elif f_name == 'max_size':
                        if int(disk['size']) > filters['max_size']:
                            all_filters_passed = False
                    elif f_name == 'rota':
                        rotational = '1' if filters['rota'] else '0'
                        if disk['rota'] != rotational:
                            all_filters_passed = False
                    elif f_name in ('name', 'name_glob'):
                        if SYS_BLOCK + disk['name'] not in glob.glob(SYS_BLOCK + filters[f_name]):
                            all_filters_passed = False
                    elif f_name == 'model_regex':
                        pattern = re.compile(filters[f_name])
                        if not pattern.search(disk['model']):
                            all_filters_passed = False
                    elif f_name == 'empty':
                        if (filters['empty'] and 'children' in disk) or \
                                (not filters['empty'] and 'children' not in disk):
                            all_filters_passed = False
                    elif f_name == 'is_mounted':
                        disk_mounted = self._tree_traverse_and_apply(disk, LsBlkWrapper._is_mounted)
                        if filters['is_mounted'] != disk_mounted:
                            all_filters_passed = False
                    elif f_name == 'ro':
                        if (filters['ro'] and disk['ro'] == '0') or (not filters['ro'] and disk['ro'] == '1'):
                            all_filters_passed = False
                    elif f_name == 'rm':
                        if (filters['rm'] and disk['rm'] == '0') or (not filters['rm'] and disk['rm'] == '1'):
                            all_filters_passed = False
                    elif str(filters[f_name]) != disk[f_name]:
                        all_filters_passed = False

            if all_filters_passed:
                result.append(disk)
        return result
