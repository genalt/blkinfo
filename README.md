# blkinfo - Block Devices Information

## Library

### About

blkinfo is a python library to list information about all available or the specified block devices.

It bases on `lsblk` command line tool, provided by `util-linux`, in addition, it collects information about block
devices, using `/sys/block`, `/sys/devices`, `/proc` directories.

The main goal is to provide Python's binding to `lsblk`. Old versions of `lsblk`, provided by `util-linux-2.23.2` on
Red Hat Enterprise Linux 7 and Centos 7 (and earlier versions) do not contain an option to output to JSON format.

Additional features to `lsblk`:

- information about iSCSI target IP address and port number was added
- block device usage statistics

### Installation

Install python's package from PyPI repository using `pip` util:

```
pip3 install blkinfo

pip install blkinfo
```


Install rpm package from Copr.

```
dnf copr enable galt/blkinfo

dnf install python2-blkinfo

dnf install python3-blkinfo
```


### Usage example


Information about all available block devices:

```python
   myblkd = BlkDiskInfo()
   all_my_disks = myblkd.get_disks()
   json_output = json.dumps(all_my_disks)
   print(json_output)
```


Passing filters as an argument to the get_disks() method:

```python
   myblkd = BlkDiskInfo()
   filters = {
      'tran': 'iscsi'
   }

   all_my_disks = myblkd.get_disks(filters)
   json_output = json.dumps(all_my_disks)
   print(json_output)
```



## Filters


-    name:      device name
-    name_glob:  globex for a device name
-    kname:      internal kernel device name
-    size:       size of the device
-    min_size:   min size for a device
-    max_size:   max size for a device
-    maj:min     major and minor device numbers
-    ra:         read-ahead device (e.g. type)
-    ro:         read-only device
-    rm:         removable device
-    hotplug:    removable or hotplug device (usb, pcmcia, ...)
-    model:      device identifier, including vendor name
-    serial:     disk serial number
-    state:      state of the device
-    hctl:       string with 'Host:Channel:Target:Lun' string (for SCSI)
-    rota:       rotational device
-    tran:       device transport type
-    iscsi_target_ip:      used together with 'tran': 'iscsi'
-    iscsi_target_port:    used together with 'tran': 'iscsi'
-    is_mounted:           does a disk have mounted partition



## Roadmap

1. Now `blkinfo` library is using `lsblk` command line tool directly.
   The good idea is to create `lsblk` core library in C and just add bindings in Python.
   https://github.com/karelzak/util-linux/issues/839



---
**NOTE**:

 If you have got a question or suggestion, please, file an issue on
GitHub or submit a PR. https://github.com/grinrag/blkinfo

---
