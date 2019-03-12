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

## Varslink Service

There is also varlink service available. To run the service:

```
cd  ./src/varlink/
python3 blkinfo_server.py --varlink="unix:@blkinfo"&
```


There are some scripts in the ./src/varlink/examples directory, with
examples of how to use the varlink service.


Also command line tool `varlink` is available from `rawhide` repository (Fedora 30 currently).
To install:

```
sudo dnf install fedora-repos-rawhide -y
sudo dnf install --enablerepo rawhide python3-varlink libvarlink-util
```


Then `varlink` cli tool can be used to call blkinfo methods:

```
varlink call unix:@blkinfo/com.redhat.blkinfo.GetDisks '{"filters": {"name": "sda"}}'

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
