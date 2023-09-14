# torf-gui

[![GitHub Build Status](https://img.shields.io/github/actions/workflow/status/SavageCore/torf-gui/build.yml?style=flat-square&logo=pytest)](https://github.com/SavageCore/torf-gui/actions/workflows/build.yml)
[![GitHub Lint Status](https://img.shields.io/github/actions/workflow/status/SavageCore/torf-gui/lint.yml?style=flat-square&logo=python&label=lint)](https://github.com/SavageCore/torf-gui/actions/workflows/lint.yml)


A quick and dirty port of
[dottorrent-gui](https://github.com/kz26/dottorrent-gui) for
[torf](https://github.com/rndusr/torf)

![image](img/screenshot_light.png)

![image](img/screenshot_dark.png)

## Features

-   Fast (capable of several hundred MB/s)
-   Cross-platform
-   Full Unicode support
-   Use multiple CPU cores to compute piece hashes
-   Automatic and manual piece size selection, up to 16MB
-   Batch torrent creation mode
-   Filename exclusion patterns (globs)
-   HTTP/web seeds support [(BEP
    19)](http://www.bittorrent.org/beps/bep_0019.html)
-   Private flag support [(BEP
    27)](http://www.bittorrent.org/beps/bep_0027.html)
-   Randomize info hash to help with cross-seeding
-   User-definable source string
-   Optional MD5 file hash inclusion
-   [Import/export of
    profiles](https://github.com/SavageCore/torf-gui/wiki/Profiles)
    (trackers, web seeds, source string, filename exclusion patterns)
-   Automatic dark mode!

## Installation

### Windows and macOS

You can find the latest releases [here](https://github.com/SavageCore/torf-gui/releases).

On Windows, simply download and run `torf-gui-win64.exe`. You may need
to download and install the [Microsoft Visual C++ Redistributable for
Visual Studio
2015](https://www.microsoft.com/en-us/download/details.aspx?id=48145).

On macOS, download and extract `torf-gui-macOS.zip` then run the app.
You may need to allow the app to run in your security settings.

### Linux

**Requirements**

-   Python 3.3+
-   PyQt5 5.7+
-   libxcb-xinerama0 (Debian/Ubuntu)

Latest stable release: `pip install torf-gui`

Development: `git clone` this repository, then `pip install .`

To run: `torf-gui`

## Portable Mode

torf-gui can be configured to run in portable mode, good for running
from USB drives and network shares. To enable this, simply create an
empty file named `torf-gui.ini` in the same directory as the main
excecutable.

## License

© 2023 Oliver Sayers. Made available under the terms of the [GNU General
Public License v3](http://choosealicense.com/licenses/gpl-3.0/).