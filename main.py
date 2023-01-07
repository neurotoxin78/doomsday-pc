import subprocess
import sys
from PyQt5 import QtCore, QtWidgets, uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStatusBar, QLabel,
                             QPushButton, QFrame, QCheckBox)
import socket
from rich.console import Console
from datetime import datetime
import json
import gc
from scan_music import scan_for_palylist
import platform


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
        self.voltage = 12.0
        uic.loadUi('main.ui', self)
        self.setWindowTitle("Doomsday-PC Launcher")
        self.setStylesheet("main.qss")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.clocktimer = QTimer()
        self.sensortimer = QTimer()
        self.sysstattimer = QTimer()
        self.powertimer = QTimer()

        self.initUI()

    def initUI(self):
        self.sensortimer.timeout.connect(self.powerMeter)
        self.sensortimer.start(1000)
        self.sysstattimer.timeout.connect(self.sysStat)
        self.sysstattimer.start(5000)
        self.clocktimer.timeout.connect(self.Clock)
        self.clocktimer.start(500)
        self.powertimer.timeout.connect(self.powerCheck)
        self.powertimer.start((1000 * 1) * 3)
        self.terminalButton.setText("Terminal")
        self.terminalButton.clicked.connect(self.LaunchTerminal)
        self.smplayerButton.setText("SMPlayer")
        self.smplayerButton.clicked.connect(self.LaunchSmplayer)
        self.w3mButton.setText("W3M")
        self.w3mButton.clicked.connect(self.LaunchW3M)
        self.toolButton_2.setText("nVLC")
        self.toolButton_2.clicked.connect(self.LaunchVLC)
        self.toolButton_3.setText("Gen m3u")
        self.toolButton_3.clicked.connect(scan_for_palylist)
        self.poweroffButton.clicked.connect(self.PowerOff)
        self.rebootButton.clicked.connect(self.Reboot)
        self.ipLabel = QLabel("Label: ")
        self.autopoweroff = QCheckBox()
        self.autopoweroff.setText("auto")
        self.pwroffButton = QPushButton()
        self.pwroffButton.setText("PowerOFF")
        self.pwroffButton.clicked.connect(self.PowerOff)
        self.ipLabel.setStyleSheet('border: 0; color:  #faac25;')
        self.statusBar.reformat()
        self.statusBar.setStyleSheet('border: 0; background-color: #faac25;')
        self.statusBar.setStyleSheet("QStatusBar::item {border: none;}")
        self.statusBar.addPermanentWidget(VLine())    # <---
        self.statusBar.addPermanentWidget(self.ipLabel)
        self.ipLabel.setText("ip:0.0.0.0")
        self.statusBar.addPermanentWidget(VLine())  # <---
        self.statusBar.addPermanentWidget(self.pwroffButton)
        self.statusBar.addPermanentWidget(VLine())  # <---
        self.statusBar.addPermanentWidget(self.autopoweroff)

    def powerCheck(self):
        if self.voltage < 10.8:
            if self.autopoweroff.isChecked():
                print("PowerOFF")
                self.PowerOff()
            else:
                print("autopoweroff disabled")
    def Clock(self):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.statusBar.showMessage(current_time)
        self.ipLabel.setText(get_ip())

    def LaunchW3M(self):
        print("run w3c")
        result = subprocess.run(["/usr/bin/kitty -e /usr/bin/w3m google.com &",], capture_output = True, text = True, shell = True)
    def Reboot(self):
        result = subprocess.run(["/usr/bin/systemctl", "reboot"], capture_output = True, text = True)
    def PowerOff(self):
        result = subprocess.run(["/usr/bin/systemctl","poweroff"], capture_output=True, text=True)
    def LaunchSmplayer(self):
        result = subprocess.run(["/usr/bin/smplayer &",], capture_output=True, text=True, shell = True)
    def LaunchVLC(self):
        result = subprocess.run(["/usr/bin/x-terminal-emulator -e /usr/bin/nvlc &",], capture_output=True, text=True, shell = True)
    def LaunchTerminal(self):
        result = subprocess.run(["/usr/bin/x-terminal-emulator &",], capture_output=True, text=True, shell = True)

    def powerMeter(self):
        if platform.system() == 'Linux':
            with open("/sys/bus/i2c/devices/0-0040/hwmon/hwmon1/in1_input") as volt:
                val = float(volt.read()) / 1000
            # auto power off
            self.voltage = val
            decor = "%.1f" % val
            volt = decor[:3]
            vmant = decor[-1]
            #print(volt, vmant)
            self.voltLabel.setText(volt)
            self.vmantLabel.setText(vmant)
            with open("/sys/bus/i2c/devices/0-0040/hwmon/hwmon1/curr1_input") as amp:
                val = float(amp.read())
            decor = "%.0f" % val
            self.amperLabel.setText(decor)
            with open("/sys/bus/i2c/devices/0-0040/hwmon/hwmon1/power1_input") as power:
                val = float(power.read()) / 1000000
            decor = "%.1f" % val
            pwr = decor[:2]
            pmant = decor[-1]
            self.pwrLabel.setText(pwr)
            self.pmantLabel.setText(pmant)
        else:
            pass
    def sysStat(self):
        if platform.system() == 'Linux':
            cpu_stat = subprocess.run(["/usr/bin/mpstat -o JSON"], capture_output = True, text = True, shell = True)
            j_data = json.loads(cpu_stat.stdout)
            statistics = j_data['sysstat']['hosts'][0]['statistics']
            cpu_load_usr = statistics[0]['cpu-load'][0]['usr']
            cpu_load_idle = statistics[0]['cpu-load'][0]['idle']
            cpu_load_sys = statistics[0]['cpu-load'][0]['sys']
            cpu_load_iowait = statistics[0]['cpu-load'][0]['iowait']
            ram_stat = subprocess.run(["/usr/bin/free -h --kilo"], capture_output = True, text = True, shell = True)
            ram = ram_stat.stdout
            # cpu string
            sys_stat = f"CPU: usr {cpu_load_usr}% sys {cpu_load_sys}% iow {cpu_load_iowait}% idle {cpu_load_idle}%\n{ram}"
            self.statLabel.setText(sys_stat)
            gc.collect()
        else:
            pass

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
