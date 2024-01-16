Changelog
=========
0.3.0
-----
* Resolved an issue that caused the application to crash when loading a file with the piece size set to a specific value, instead of automatic
* Added support for 64MB piece sizes
* Support sub-folders in batch mode
* General styling improvements

0.2.6
-----
* Support for torf 4.2.4 (32MB piece size support)
* Better handling of piece size selection when switching between modes

0.2.5
-----
* Fix crash when choosing a folder in batch mode with no files in it

0.2.4
-----
* [Windows] Ensure the title bar is dark when system theme is dark

0.2.3
-----
* Fix for pieces and size being reversed under torrent options

0.2.2
-----
* Fix PyPI build/release - new filename needed

0.2.1
-----
* Fix batch torrent creation

0.2.0
-----
* Upgrade all dependencies to latest versions
* Removed torf.exceptions within code as that does not exist

0.1.0
-----
* Initial release
