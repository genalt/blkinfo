import os
import subprocess
import json
import glob
import re


SYS_DEV = '/sys/devices/'
SYS_BLOCK = '/sys/block/'
ISCSI_TARGET_PATH = SYS_DEV + 'platform/%s/%s/%s/iscsi_connection/%s'  # host, session, connection, connection


# list of main filters available for `lsblk`,
# see docs of lsblk for more details
#    name:    device name
#    kname:   internal kernel device name
#    size:    size of the device
#    maj:     major device number
#    min:     minor device number
#    ra:      read-ahead device (e.g. type)
#    ro:      read-only device
#    rm:      removable device
#    hotplug: removable or hotplug device (usb, pcmcia, ...)
#    model:   device identifier, including vendor name
#    serial:  disk serial number
#    state:   state of the device
#    hctl:    string with 'Host:Channel:Target:Lun' string (for SCSI)
#    rota:    rotational device
#    tran:    device transport type
#    ...

# sometimes we would like to have a range for some parameter
# or regex or glob instead of exact name
# for these purposes we need to use additional filter name
ADDITIONAL_DISK_FILTER = ['min_size', 'max_size', 'name_glob', 'model_regex', 'remote',
                          'empty', 'is_mounted']


class BlkFilterPartition(object):
    """Class to hold general information about a partition of a block device"""

    def __init__(self):
        self.fstype = None       # filesystem type
        self.mountpoint = None   # where the device is mounted
        self.label = None        # filesystem label
        self.uuid = None         # filesystem UUID
        self.parttype = None     # partition type UUID
        self.partlabel = None    # partition LABEL
        self.partuuid = None     # partition UUID


class BlkDeviceInfo(object):
    """ BlkDeviceInfo is a class to provide basic information about:
        - Disks available in the system and different parameters related to block devices
        - Partitions and information about filesystem type, encription, MD raid, free space, etc

        with flexible filtering options.
    """


    def __init__(self):
        # this DS is used for block devices (disks) processing
        self.blkdev_tree_list = BlkDeviceInfo._get_device_tree_list()

        # these DSs are used for partitions processing
        self.blkdev_rtree_list = BlkDeviceInfo._get_device_reversetree_list()
        self.blkdev_list = BlkDeviceInfo._get_device_list()

    @staticmethod
    def _get_device_tree_list():
        """ Method to provide information about all disks available in the system
            in a forest view, each physical device (a disk) is a root of corresponding tree.
        """

        # internally lsblk uses /sys/block and /sys/devices directories to get information
        # about all disks and partitions
        # TODO: rewrite without using lsblk utility

        try:
            devtree_json = subprocess.check_output(['lsblk', '-i', '-a', '-b', '-O', '-J'])
            devtree_dict = json.loads(devtree_json, encoding="ascii")

            # Add parameters or tune that ones returned by lsblk
            for d in devtree_dict['blockdevices']:

                if d['tran'] == 'iscsi':
                    d['remote'] = True

                    # add target IP address and port number for iSCSI devices
                    iscsi_disk_path = os.readlink(SYS_BLOCK + d['name'])
                    host = iscsi_disk_path.split("/")[3]
                    session = iscsi_disk_path.split("/")[4]
                    connection = glob.glob(SYS_DEV + 'platform/' + host +
                                                 '/' + session + '/connection*')[0].split('/')[-1]

                    try:
                        with open((ISCSI_TARGET_PATH % (host, session, connection, connection)) + '/address' ) as adr:
                            d['iscsi_target_ipaddr'] = adr.read().strip()
                    except IOError:
                            d['iscsi_target_ipaddr'] = None

                    try:
                        with open((ISCSI_TARGET_PATH % (host, session, connection, connection)) + '/port' ) as port:
                            d['iscsi_target_port'] = port.read().strip()
                    except IOError:
                            d['iscsi_target_port'] = None

                elif d['tran'] == 'fc':
                    d['remote'] = True
                else:
                    d['remote'] = False

                # FIXME: for some devices we have got vendor ID, instead of vendor name
                # for example for nvme disc with PCIE controller
                # to get a vendor name we need to parse 'hwdata' file.
                # As a workaround combine vendor name and model, which usually also contains
                # mention of vendor name
                d['model'] = str(d['vendor']).strip() + ' ' + str(d['model']).strip()
                d['vendor'] = d['model']

        except (subprocess.CalledProcessError, ValueError):
            return []

        return devtree_dict['blockdevices']

    @staticmethod
    def _get_device_reversetree_list():
        """ Method to provide information about all partitions of all disks available in the system
            in a forest view, where each partition is a root of corresponding tree.
            Every level of such tree contains only one leaf - parent partition of disk if this is a
            leaf of a tree.
        """

        # comment from lsblk source:
        # * The /sys/block contains only root devices, and no partitions. It seems more
        # * simple to scan /sys/dev/block where are all devices without exceptions to get
        # * top-level devices for the reverse tree.
        # option '-s' for inverse tree
        # TODO: rewrite without using lsblk utility

        try:
            devrtree_json = subprocess.check_output(['lsblk', '-i',  '-a', '-s', '-b', '-O', '-J'])
            devrtree_dict = json.loads(devrtree_json, encoding="ascii")
        except (subprocess.CalledProcessError, ValueError):
            return []

        return devrtree_dict['blockdevices']

    @staticmethod
    def _get_device_list():
        """ Method to provice a list of all devices and partitions.
            Every element of the list is a dictionary like name -> information
        """
        try:
            devlist_json = subprocess.check_output(['lsblk', '-i', '-l',  '-a', '-b', '-O', '-J'])
            devlist_dict = json.loads(devlist_json, encoding="ascii")
        except (subprocess.CalledProcessError, ValueError):
            return []

        return devlist_dict['blockdevices']

    @staticmethod
    def _tree_traverse_and_apply(node, method, additional_arg_list=None):

        # Preorder traversal, first check current node
        # then all its children. I method() ruturns True, we need to stop
        if additional_arg_list:
            stop_result = method(node, additional_arg_list)
        else:
            stop_result = method(node)
        if stop_result:
            return stop_result

        if 'children' in node:
            for c in node['children']:
                stop_result = BlkDeviceInfo._tree_traverse_and_apply(c, method, additional_arg_list)
                if stop_result:
                    return stop_result

        return False


    @staticmethod
    def _is_mounted(blkdev_info_dict):
        """Method to check if partition is mounted"""
        if blkdev_info_dict['mountpoint'] is not None:
            return True
        return False

    def get_partition_list(self, filters):
        result = []
        return result

    def get_disk_list(self, filters):
        result = []

        if not self.blkdev_tree_list:
            return result

        # iterate through all disks in the system
        for disk in self.blkdev_tree_list:

            all_filters_passed = True

            disk['size'] = disk['size'] or 0

            print(disk['name'])

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
                        disk_mounted = BlkDeviceInfo._tree_traverse_and_apply(disk, BlkDeviceInfo._is_mounted)
                        if filters['is_mounted'] != disk_mounted:
                            all_filters_passed = False
                    elif str(filters[f_name]) != disk[f_name]:
                        all_filters_passed = False

            if all_filters_passed:
                print("add current disk into result")
            else:
                print("ignore current disk")
        return result
