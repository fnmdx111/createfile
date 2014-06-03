
createfile
====

Deploy
----
Download [`bundle.7z`](https://www.dropbox.com/s/gxdtzjc49tkzf2i/bundle.7z )
and extract it into anywhere you like.
Make sure you have Python3 installed. If not, go to
[python.org](https://www.python.org/ ) and download the latest version of
Python *x64*.
Then read `README.md` in `bundle.7z`.

How to run
----
First activate the virtualenv we created earlier, using
`path/to/your/env/Scripts/activate.bat`.
Then under project root directory, run `python main.py`. You may want
to redirect the output to a text file, in this case, use
`python main.py > a.txt`.
Don't forget to modify the path to the disk image.

Making your own disk image
----
Install VirtualBox and use
`VBoxManage internalcommands converttoraw path/to/your/vdi.vdi output.raw`

Configuring and using the web interface
----
Go to subdirectory `web` and read the `README.md` there.

Cookbook
----
* To use a partition image:
```python
from stream.img_stream import ImageStream
from drive.fs.fat32 import get_fat32_partition

with ImageStream(path_to_partition_image) as stream:
    partition = get_fat32_partition(stream)
    files, dirs = partition.get_fdt()
```
* To use a disk image:
```python
from stream.img_stream import ImageStream
from drive.disk import get_drive_obj

with ImageStream(path_to_disk_image) as stream:
    for partition in get_drive_obj(f):
        if partition:
            if partition.type == FAT32.type:
                files, dirs = partition.get_fdt()
```

* To use a real disk: replace `from stream.img_stream import ImageStream` to
`from stream.windows_drive import WindowsPhysicalDriveStream` and also replace
the parameter of the `with` statement. Make sure the argument to
`WindowsPhyscialDriveStream` represent the hard disk you want to read.

* To get filename and data runs from an MFT record:
```python
FILENAME_ATTR_TYPE = 0x30
DATA_ATTR_TYPE = 0x80
if FILENAME_ATTR_TYPE in mft.attributes:
    print('filename: %s' % mft.attributes[FILENAME_ATTR_TYPE].filename)
if DATA_ATTR_TYPE in mft.attributes:
    print('data runs: %s' % mft.attributes[DATA_ATTR_TYPE].data_runs)
```


Licensing
====

Licenced under GNU LGPLv3.

