import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtWidgets import QApplication, QMainWindow

from torf_gui import __version__
from torf_gui.ui_mainwindow import Ui_MainWindow

PROGRAM_NAME = "torf-gui"
PROGRAM_NAME_VERSION = f"{PROGRAM_NAME} {__version__}"

# Create an instance of the application
app = QApplication(sys.argv)

# Create a QMainWindow and set up the Ui_MainWindow in it
main_window = QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(main_window)
# Set the window title
main_window.setWindowTitle(PROGRAM_NAME_VERSION)


# Function to take screenshot
def take_screenshot():
    # Grab the screen that contains the window
    screen = QGuiApplication.screenAt(main_window.geometry().center())
    if screen is not None:
        # Grab the entire screen and crop it to the window geometry
        screenshot = screen.grabWindow(QApplication.desktop().winId())
        cropped_screenshot = screenshot.copy(main_window.frameGeometry())
        # Save the cropped screenshot to a file
        cropped_screenshot.save("screenshot-light.png", "png")
    # Quit the application
    QApplication.quit()


# Set a timer to take the screenshot after 5 seconds
QTimer.singleShot(5000, take_screenshot)

# Start the application
main_window.show()
sys.exit(app.exec_())
