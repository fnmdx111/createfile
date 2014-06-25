
Web Interface for createfile
====

Currently this includes cluster - time plot which displays cluster
distribution over time and first cluster - time plot which displays the
distribution of first cluster number over time.

Configuring
----
Please create a file named `config.py` although there's nothing much to be
configured. Following is the default configuration:
```python
# encoding: utf-8
import logging
from stream import ImageStream, WindowsPhysicalDriveStream

stream = ImageStream('d:/flash.raw')
address, port = '127.0.0.1', 8000

partition_log_level = logging.INFO
```

Run
----
Run `bootstrap.py` located in the parent directory and
visit `http://127.0.0.1:8000/index` to see cluster - time view.
On the page the server returned, there's an input box named `Stream uri`,
where you input the stream whose ct view you'd like to see.

The uri scheme is:
* For `WindowsPhysicalDriveStream`, the uri is `W:n`, where n is the argument
to the constructor of `WindowsPhysicalDriveStream`
* For `ImageStream`, the uri is `I:path`, where path is the path to the image
file. E.g. `I:d:\flash.raw`.

Dependency
----
This web interface make use of the following component:
* Flask
* Flotr2
* jQuery
* Node.js
* Coffeescript

Normally, this will run without any building.
But it does require Flask installed to provide the framework on which this
application runs. To install Flask, see the Deploy section of the main
`README.md`.

