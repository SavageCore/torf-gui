import pytest
import sys
from PyQt5 import QtCore, QtWidgets
from pytestqt.qtbot import QtBot
from torfGUI.gui import TorfGUI
from torfGUI import __version__

PROGRAM_NAME = "torf-gui"
PROGRAM_NAME_VERSION = "{} {}".format(PROGRAM_NAME, __version__)

@pytest.fixture
def app(qtbot: QtBot):
    # Setup
    torf = TorfGUI()
    MainWindow = QtWidgets.QMainWindow()

    # Get the QWidget
    torf.setupUi(MainWindow)
    qtbot.addWidget(MainWindow)

    MainWindow.setWindowTitle(PROGRAM_NAME_VERSION)
    MainWindow.show()

    import os
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
    if not os.path.exists("tmp/test_dir"):
        os.makedirs("tmp/test_dir")

    # Create a directory of files to use for testing
    with open("tmp/test_dir/test_file.iso", "w") as f:
        f.write("test")
    with open("tmp/test_dir/test_file.txt", "w") as f:
        f.write("test")

    # Run
    yield torf

# GUI loads
def test_load(app):
    assert app is not None

# GUI loads with correct title
def test_title(app):
    assert app.MainWindow.windowTitle() == PROGRAM_NAME_VERSION

# Batch mode checkbox appears when Directory is selected
def test_batch_checkbox(app, qtbot):
    assert app.batchModeCheckBox.isVisible() == False

    qtbot.mouseClick(app.directoryRadioButton, QtCore.Qt.LeftButton)

    assert app.batchModeCheckBox.isVisible()

# Piece size is disabled when Directory Batch mode is selected
def test_piece_size(app, qtbot):
    assert app.pieceSizeComboBox.isEnabled()

    qtbot.mouseClick(app.directoryRadioButton, QtCore.Qt.LeftButton)
    qtbot.mouseClick(app.batchModeCheckBox, QtCore.Qt.LeftButton)
    assert app.pieceSizeComboBox.isEnabled() == False

# Reset button resets the GUI
def test_reset(app, qtbot):
    qtbot.mouseClick(app.directoryRadioButton, QtCore.Qt.LeftButton)
    assert app.directoryRadioButton.isChecked()

    qtbot.mouseClick(app.resetButton, QtCore.Qt.LeftButton)

    assert app.directoryRadioButton.isChecked() == False

# Create button is disabled when no input is given
def test_create_button_disabled(app, qtbot):
    assert app.inputEdit.text() == ""
    assert app.createButton.isEnabled() == False

    app.inputEdit.setText("tmp/test_dir/test_file.txt")
    app.initializeTorrent()

    assert app.createButton.isEnabled()

# Piece size is calculated correctly for a file
def test_piece_size_file(app, qtbot):
    app.inputEdit.setText("tmp/test_dir/test_file.txt")
    app.initializeTorrent()

    assert app.pieceCountLabel.text() == "16384 pieces @ 1 byte each"

# File size is calculated correctly for a file
def test_file_size_file(app, qtbot):
    app.inputEdit.setText("tmp/test_dir/test_file.txt")
    app.initializeTorrent()

    assert app.MainWindow.statusBar().currentMessage() == "test_file.txt: 4 bytes"

# File size is calculated correctly for a folder
def test_file_size_file(app, qtbot):
    app.inputEdit.setText("tmp/test_dir")
    app.initializeTorrent()

    assert app.MainWindow.statusBar().currentMessage() == "test_dir: 8 bytes"

# # Options are remembered when re-opening the app
# def test_options_remembered(app, qtbot):
