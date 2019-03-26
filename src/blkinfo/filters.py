import glob
import re

from .wrappers import LsBlkWrapper, DISK_TYPES, DISK_FILTERS, ADDITIONAL_DISK_FILTER, SYS_BLOCK


class BlkDiskInfo(LsBlkWrapper):
    """ BlkDeviceInfo is a class to provide basic information about
        disks available in the system and different parameters related to block devices
    """

    def get_disks(self, filters=None):
        result = []
        if not self._disks:
            return result

        if not filters:
            filters = []

        raid_added = set()

        # iterate through all disks in the system
        for dn in self._disks:
            disk = self._disks[dn]
            if disk['type'] not in DISK_TYPES:
                continue

            if 'show_raid' in filters and filters['show_raid']:
                if len(disk['children']) == 1:
                    child_name = disk['children'][0]
                    if child_name in raid_added:
                        continue
                    child_type = self._disks[child_name]['type']

                    # child is raid
                    if child_type.startswith('raid'):
                        disk = self._disks[child_name] # show raid info instead of parent disk
                        raid_added.add(child_name)

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
                        if (filters['empty'] and 'children' in disk) or (not filters['empty'] and 'children' not in disk):
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
