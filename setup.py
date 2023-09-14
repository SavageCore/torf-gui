from setuptools import find_packages, setup

with open("torfGUI/version.py") as f:
    exec(f.read())

setup(
    name="torf-gui",
    version=__version__,
    packages=find_packages(),
    entry_points={"gui_scripts": ["torf-gui = torfGUI.gui:main"]},
    install_requires=[
        "torf>=4.2.2",
        "humanfriendly>=10.0",
        "PyQt5>=5.15.9",
        "pyqtdarktheme>=2.1.0",
    ],
    # metadata for upload to PyPI
    author="Oliver Sayers",
    author_email="talk@savagecore.uk",
    description=(
        "An advanced GUI torrent file creator with batch functionality, "
        "powered by PyQt and torf."
    ),
    long_description=open("README.md").read(),
    keywords="bittorrent torrent",
    url="https://github.com/SavageCore/torf-gui",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
