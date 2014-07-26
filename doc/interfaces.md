
二次开发指南
====

drive包
----

`drive.fs`是本系统中FAT32文件系统和NTFS文件系统的驱动程序所在包，`drive.fs.fat32.FAT32`与`drive.fs.ntfs.NTFS`类分别代表FAT32与NTFS文件系统。它们继承自`drive.fs.Partition`抽象类，这个类包括一个抽象方法`Partition.get_entries`。如果想要实现新的文件系统，请继承`drive.fs.Partition`，并实现其中的`Partition.get_entries`方法。

`Partition.__init__`签名如下：
* `type_`: 文件系统类型名称，如`'FAT32'`、`'NTFS'`等
* `stream`: 数据流，应是`stream.ImageStream`或`stream.WindowsPhysicalDriveStream`或它们的子类
* `preceding_bytes`: 文件系统数据开始的偏移地址（单位：字节）
* `boot_sector_parser`: 引导扇区解析器，应是支持`parse_stream(stream_like)`方法的对象，如`construct.Struct`
* `ui_handler`: 已弃用

在继承Partition类之后，应该实现一个包装函数，并用`drive.type.register`装饰这个包装函数，这样在使用内置的`get_drive_obj`生成器枚举数据流上的所有分区时，就能自动调用对应的文件系统类了。这个包装函数的签名应为：
* `entry`: MBR中的分区项，最好支持字典协议
* `stream`: 数据流，与`Partition.__init__:stream`相同
* `ui_handler`: 已弃用

`Partition.get_entries`签名如下：
* 无参数
* 返回值: 该方法应当创建一个`pandas.DataFrame`对象，将文件系统的文件项目信息装入这个对象中并返回该对象

一般来讲，`Partition.get_entries`返回的DataFrame对象应有以下几列：

|`is_directory`  |`full_path`           |`id`       |
|:--------------:|:--------------------:|:---------:|
|该文件项是否是文件夹|该文件项所代表文件的绝对路径|该文件项的序号|

用户在使用`Partition.get_entries`获得DataFrame对象后，可以使用DataFrame对象所自带的功能，如输出到Excel电子表格，输出到csv文件等。具体请查阅pandas的相关文档。

请参阅`drive.fs.fat32.__init__.py:get_fat32_obj`，`drive.fs.fat32.structs.py:FAT32BootSector`，`drive.fs.fat32.structs.py:FAT32`。


judge包
----

为了实现时间规则DSL所表达不出来的语义（如look-ahead、look-behind模式），有Python经验的高级用户可以利用judge提供的二次开发接口，实现扩展的Rule类，以在规则判断中获得Python所提供的表达能力。

为了扩展Rule类，用户需要继承`judge.Rule`类，并重载`Rule.do_apply`方法，新建的模块应放入`judge.ext`包中，并且类需要用`judge.ext.register`装饰，以自动注册到规则表中。

用户在继承Rule时，必须：
* 指定类变量`name`: 该规则的名称（如果使用图形界面，则该名称将显示在规则列表中）
* 指定类变量`type`: 该规则适用的文件系统类型名（如`'FAT32'`等）
* 指定类变量`conclusion`: 该规则的结论（如果使用图形界面，则该名称将显示在规则列表中）
* 指定类变量`abnormal`: 如果指定为True，则符合该规则的文件项目会被标记为异常文件项目；反之则不会

用户同时必须重载`Rule.do_apply`，该方法签名如下：
* `entries`: 一个`pandas.DataFrame`对象，装载了所有要检查的文件项

用户应在`Rule.do_apply`中进行规则的判定，同时对阳性的文件项序号进行标记。标记文件项序号应使用方法`Rule.mark_as_positive`，其签名如下：
* `i`: 整数，表示要标记的文件项的序号

请注意，如果在`Rule.do_apply`中，用户对entries进行了修改（如过滤，排序等）操作，则应调用一次`self._pending_return_values`，以使返回值缓存获得更新，其签名如下：
* `entries`: 修改后的DataFrame对象

请参阅`judge.Rule`，`judge.ext.TimelineRule`，`judge.ext.SNEq1Rule`。

stream包
----

用户在对本系统进行二次开发时，可以使用stream包内提供的`ImageStream`类和`WindowsPhysicalDriveStream`类，它们分别提供了对镜像文件和物理驱动器的数据流化。它们支持有限的`file`对象协议，如下：
* `read(size=None)`: 读取并返回size大小的数据，如果size为None，则读取并返回默认读缓冲大小的数据
* `seek(pos, whence)`: 设置流指针以whence方式移动到pos处，请参阅Python文档中对`io.IOBase.seek`的说明
* `close`: 关闭流



