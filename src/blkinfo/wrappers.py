import os
import glob
import subprocess



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

DISK_FILTERS = ['name', 'kname', 'fstype', 'label', 'mountpoint', 'size', 'maj:min', 'rm',
                'model', 'vendor', 'serial','hctl', 'tran', 'rota', 'type', 'ro', 'owner',
                'group', 'mode']


# sometimes we would like to have a range for some parameter
# or regex or glob instead of exact name
# for these purposes we need to use additional filter name
ADDITIONAL_DISK_FILTER = ['min_size', 'max_size', 'name_glob', 'model_regex', 'remote',
                          'empty', 'is_mounted']

DISK_TYPES = ['disk', 'rom', 'mpath']




class LsBlkWrapper(object):
    """ LsBlkWrapper is a wrapper for 'lsblk' command line tool provided by util-linux
        It parses output of lsblk, builds block devices hierarchy in the system,
        fills self.disk_info with different block device information
    """

    def __init__(self):
        self.disk_tree = LsBlkWrapper._build_disk_tree()
        self._add_iscsi_info(self.disk_tree)
        self._merge_model_vendor(self.disk_tree)

    @staticmethod
    def _merge_model_vendor(disk_tree):
        # FIXME: for some devices we have got vendor ID, instead of vendor name
        # for example for nvme disc with PCIE controller
        # to get a vendor name we need to parse 'hwdata' file.
        # As a workaround combine vendor name and model, which usually also contains
        # mention of vendor name
        for d in disk_tree:
            disk_tree[d]['model'] = str(disk_tree[d]['vendor']).strip() + ' ' + str(disk_tree[d]['model']).strip()
            disk_tree[d]['vendor'] = disk_tree[d]['model']

    @staticmethod
    def _add_iscsi_info(disk_tree):
        """ add target IP address and port number for iSCSI devices """

        for name in disk_tree:
            d = disk_tree[name]
            if d['type'] != 'disk' or d['tran'] != 'iscsi':
                continue

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

    @staticmethod
    def _get_disk_level(lsblk_disk_line):
        """ Helper to parse disk hierarchy returned by 'lsblk' """
        level = 0
        for c in lsblk_disk_line:
            if c in ['`', '|', '-', ' ']:
                level = level + 1
            else:
                break
        return level, lsblk_disk_line[level:]

    @staticmethod
    def _build_disk_tree():
        """ Build Block device tree and gather information
            about all disks and partitions avaialbe in the system
        """

        disk_tree = {}
        try:
            filter_str = ','.join(DISK_FILTERS).upper()
            disk_info_list = subprocess.check_output(['lsblk', '-a', '-n', '-r', '-b', '-o', filter_str])

            for di in disk_info_list.split(b'\n')[:-1]:
                params = [p.decode("unicode_escape").strip() for p in di.split(b' ')]
                dn = params[0]  # disk name
                disk_tree[dn] = dict(zip(DISK_FILTERS, params))
                disk_tree[dn]['children'] = []
                # for some devices we have empty size field,
                # use 0 instead
                disk_tree[dn]['size'] = disk_tree[dn]['size'] or 0

        except (subprocess.CalledProcessError, ValueError):
            return {}

        # parse output of lsblk to build tree hierarchy
        disk_hierarchy = subprocess.check_output(['lsblk', '-a', '-n', '-i', '-o',  'NAME'])
        parent_stack = []
        for disk_line in disk_hierarchy.split(b'\n'):
            level, name = LsBlkWrapper._get_disk_level(disk_line)

            while parent_stack:
                p = parent_stack.pop()
                if p[1] < level:
                    disk_tree[p[0]]['children'].append(name)
                    parent_stack.append(p)
                    break

            parent_stack.append([name, level])

        return disk_tree


    def _tree_traverse_and_apply(self, node, method, additional_arg_list=None):
        """ Preorder traversal for device tree and applying custom method on every
            node, until custom method returns True
        """

        # Preorder traversal, first check current node
        # then all its children. I method() ruturns True, we need to stop
        if additional_arg_list:
            stop_result = method(node, additional_arg_list)
        else:
            stop_result = method(node)

        if stop_result:
            return stop_result

        if node['children']:
            for child_name in node['children']:
                child_node = self.disk_tree[child_name]
                stop_result = LsBlkWrapper._tree_traverse_and_apply(child_node, method, additional_arg_list)
                if stop_result:
                    return stop_result

        return False

    @staticmethod
    def _is_mounted(blkdev_info_dict):
        """Method to check if partition is mounted"""
        if blkdev_info_dict['mountpoint'] is not None:
            return True
        return False
