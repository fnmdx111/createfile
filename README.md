
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

Using gui
----
Run `bootstrap.py` after you activate your virtualenv.

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

* To plot an FAT32 partition:
```python
from drive.fs.fat32 import plot_fat32

entries = filter_entries() # filter the entries per your will

plot_fat32(entries)
```

Statistical metrics
----
Recently a new branch `statistics` is merged into `master`, which contains
new method using normalized Kendall's tau score and Spearman's rho score to
help accomplishing the project's goal.


Minimal dependencies
----

* scipy (mainly used in stats)
* numpy (dependency of various libraries)
* matplotlib (used in plotting)
* pyparsing (dependency of matplotlib)
* PySide (for gui)
* Jinja2 (for timeline template rendering)
* MarkupSafe (dependency of Jinja2)
* constructs (mainly used in package drive for binary parsing)
* PyWin32 (mainly used in streaming physical drive)
* pandas (mainly used in encapsulating file entries of partitions)
* python-dateutil (dependency of pandas)
* pytz (dependency of pandas)
* six (library providing compatibility, dependency of various libraries)
* Cython (optional, used for compiling speed-up modules for various packages)

Thanks
----
The NTFS driver in package `drive.fs.ntfs` utilizes the project
[INDXParse](https://github.com/williballenthin/INDXParse ) from Willi Ballenthin.

**Thanks a lot.**

Licensing
====

Licenced under GNU LGPLv3.

