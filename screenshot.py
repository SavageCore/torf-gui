import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from torf_gui.gui import TorfGUI

# Create an instance of the application
app = QApplication(sys.argv)

# Create an instance of the main window class, set up its UI, and show it
main_window = TorfGUI()
main_window.setupUi(main_window)
main_window.show()

# Set a timer to take the screenshot after 5 seconds
QTimer.singleShot(5000, main_window.take_screenshot)

# Start the application
sys.exit(app.exec_())
