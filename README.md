# Block Devices Information

## About

blkinfo is a python package to list information about all available or the specified block devices.

It bases on `lsblk` command line tool, provided by `util-linux`, in addition it collects information about block
devices, using `/sys/block`, `/sys/devices`, `/proc` directories.

The main goal is to provide Python's binding to `lsblk`. Old verstions of `lsblk`, provided by `util-linux-2.23.2` on
Red Hat Interprise Linux 7 and Centos 7 (and earlier versions) do not contain option to output to JSON format.

Additional features to `lsblk`:

- information about iSCSI target IP address and port number was added
- block device usage statistics

## Installation

Install package from PyPI repository using `pip` util

```
pip3 install blkinfo
```



## Usage example


Information about all available block devices:

```python
   myblkd = BlkDiskInfo()
   all_my_disk = myblkd.get_disk_list()
   json_output = json.dumps(all_my_disk)
   print(json_output)
```


Passing filters as an argument to the get_disk_list() method:

```python
   myblkd = BlkDiskInfo()
   filters = {
      'tran': 'iscsi'
   }

   all_my_disk = myblkd.get_disk_list(filters)
   json_output = json.dumps(all_my_disk)
   print(json_output)
```


## Filters


-    name:      device name
-    name_glob:  globex for a device name
-    kname:      internal kernel device name
-    size:       size of the device
-    min_size:   min size for a device
-    max_size:   max size for a device (inlusive)
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
-    is_mounted:           does a disk have mounted partion




