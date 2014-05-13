
Web Interface for createfile
====

Currently this includes only cluster - time view which displays cluster
distribution over time.

Configuring
----
There's nothing much to be configured, however if you want to use default
stream or modify server address and port, go to `config.py` and modify them
respectively.

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

