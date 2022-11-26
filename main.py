import subprocess
import sys
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStatusBar, QLabel,
                             QPushButton, QFrame)
import socket
import random
import string
from rich.console import Console
from datetime import datetime

con = Console()

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

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
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.clocktimer = QTimer()
        self.sensortimer = QTimer()
        self.ipLabel = QLabel("Label: ")
        self.ipLabel.setStyleSheet('border: 0; color:  #6395ff;')
        self.statusBar.reformat()
        self.statusBar.setStyleSheet('border: 0; background-color: #6395ff;')
        self.statusBar.setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar.addPermanentWidget(VLine())    # <---
        self.statusBar.addPermanentWidget(self.ipLabel)
        self.ipLabel.setText("ip:0.0.0.0")

        self.initUI()

    def initUI(self):
        self.sensortimer.timeout.connect(self.powerMeter)
        self.sensortimer.start(500)
        self.clocktimer.timeout.connect(self.Clock)
        self.clocktimer.start(500)

        self.terminalButton.setText("Term")
        # self.terminalButton.setIcon(QIcon("close.png"))
        self.terminalButton.clicked.connect(self.LaunchTerminal)
        self.menuButton.setText("...")
        self.menuButton.clicked.connect(self.ShowMenu)
        self.poweroffButton.clicked.connect(self.PowerOff)
        self.rebootButton.clicked.connect(self.Reboot)

    def Clock(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.statusBar.showMessage(current_time)
        #hostname = socket.gethostname()
        #ipaddr = socket.gethostbyname(hostname)
        self.ipLabel.setText(get_ip())

    def Reboot(self):
        result = subprocess.run(["/usr/bin/systemctl", "reboot"], capture_output = True, text = True)
    def PowerOff(self):
        result = subprocess.run(["/usr/bin/systemctl","poweroff"], capture_output=True, text=True)
    def ShowMenu(self):
        pass
    def LaunchTerminal(self):
        result = subprocess.run(["/usr/bin/x-terminal-emulator",], capture_output=True, text=True)

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
        result = subprocess.run(["/usr/bin/mpstat", "-u", "-n" ], capture_output = True, text = True)
        self.statLabel.setText(result.stdout)

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
