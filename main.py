import sys
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt, QTimer
import random
import string
from rich.console import Console

con = Console()

def extended_exception_hook(exec_type, value, traceback):
    # Print the error and traceback
    con.log(exec_type, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exec_type, value, traceback)
    sys.exit(1)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Load the UI Page
        self.config = None
        uic.loadUi('main.ui', self)
        self.setWindowTitle("Doomsday-PC Launcher")
        self.setStylesheet("main.qss")
        self.initUI()

    def initUI(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.powerMeter)
        self.timer.start(200)

    def powerMeter(self):
        with open("/sys/bus/i2c/devices/0-0040/hwmon/hwmon1/in1_input") as volt:
            val = float(volt.read()) / 1000
        decor = "%.2f V" % val
        self.voltLabel.setText(decor)
        with open("/sys/bus/i2c/devices/0-0040/hwmon/hwmon1/curr1_input") as amp:
            val = float(amp.read())
        decor = "%.0f mA" % val
        self.amperLabel.setText(decor)
        with open("/sys/bus/i2c/devices/0-0040/hwmon/hwmon1/power1_input") as power:
            val = float(power.read()) / 1000000
        decor = "%.2f W" % val
        self.pwrLabel.setText(decor)

    def setStylesheet(self, filename):
        with open(filename, "r") as fh:
            self.setStyleSheet(fh.read())

    def exitApp(self):
        pass


def main():
    sys._excepthook = sys.excepthook
    sys.excepthook = extended_exception_hook
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
