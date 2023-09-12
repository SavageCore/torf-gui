from setuptools import setup, find_packages

with open('torfGUI/version.py') as f:
	exec(f.read())

setup(
    name="torf-gui",
    version=__version__,
    packages=find_packages(),
    entry_points={
        'gui_scripts': [
            'torf-gui = torfGUI.gui:main'
        ]
    },

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['torf>=4.2.2', 'humanfriendly', 'PyQt5>=5.7', 'pyqtdarktheme>=2.1.0'],

    # metadata for upload to PyPI
    author="Oliver Sayers",
    author_email="talk@savagecore.uk",
    description="An advanced GUI torrent file creator with batch functionality, powered by PyQt and torf.",
    long_description=open('README.rst').read(),
    keywords="bittorrent torrent",
    url="https://github.com/SavageCore/torf-gui",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ]
)
