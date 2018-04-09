#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess
import sys
import wmi
from PyQt5 import QtWidgets, uic
from os import path
from collections import namedtuple, OrderedDict


qtCreatorFile = "mainwindow.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DicGui(QtWidgets.QMainWindow, Ui_MainWindow):
    disc_profiles = {}
    no_drives = "No optical drives found"
    profile = namedtuple("Profile", "disc_type extra_options")

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # TODO - Read these from JSON or something more modular
        profiles = {"Sony PlayStation": self.profile('cd', ['/c2', '/nl']),
                    "Sony PlayStation 2 (CD)": self.profile('cd', ['/c2']),
                    "Sony PlayStation 2 (DVD)": self.profile('dvd', []),
                    "Audio CD": self.profile('cd', ['/c2'])}

        self.disc_profiles = OrderedDict(sorted(profiles.items(), key=lambda t: t[0]))

        c = wmi.WMI()
        drives = []
        for cdrom in c.Win32_CDROMDrive():
            drives.append(str(cdrom.Drive) + ' [' + str(cdrom.Caption) + ']')
        if not drives:
            self.driveLetter.addItems([self.no_drives])
        else:
            self.driveLetter.addItems(drives)

        self.discType.addItems(self.disc_profiles)
        self.start.clicked.connect(self.run_dic)
        self.browseOutputDir.clicked.connect(self.browse_directory)
        self.rb_speed4.setChecked(True)

    def browse_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                               'Choose directory',
                                                               path.expanduser(self.outputDirectory.text()))

        if directory is not "":
            self.outputDirectory.setText(directory)

    def get_file_name(self):
        if self.outputFileName.text() != "":
            # TODO - Check for illegal characters
            if not self.outputFileName.text().endswith('.bin'):
                return self.outputFileName.text() + '.bin'
            else:
                return self.outputFileName.text()
        self.statusBar.showMessage("Output file name is malformed. Aborting!")
        return None

    def get_output_directory(self):
        if self.outputDirectory.text() != "":
            expanded_path = path.expanduser(self.outputDirectory.text())
            if path.isdir(expanded_path):
                return expanded_path
        self.statusBar.showMessage("Output directory is malformed. Aborting!")
        return None

    def get_drive_letter(self):
        if self.driveLetter.currentText() is not self.no_drives:
            # TODO - Split this by colon instead
            return self.driveLetter.currentText()[0]

    def get_drive_speed(self):
        if self.rb_speed4.isChecked():
            return 4
        elif self.rb_speed8.isChecked():
            return 8
        elif self.rb_speed16.isChecked():
            return 16
        elif self.rb_speed48.isChecked():
            return 48
        elif self.rb_speedcustom.isChecked():
            if self.customDriveSpeed.text() != "":
                if self.customDriveSpeed.text().isdigit():
                    return int(self.customDriveSpeed.text())
        self.statusBar.showMessage("Drive speed is not a number. Aborting!")
        return None

    def get_disc_type(self):
        return self.disc_profiles[self.discType.currentText()].disc_type

    def get_options(self):
        if self.disc_profiles[self.discType.currentText()].extra_options:
            return self.disc_profiles[self.discType.currentText()].extra_options
        else:
            return None

    def create_commandline(self):
        if path.isfile("Release_ANSI\DiscImageCreator.exe"):
            command = [path.abspath("Release_ANSI\DiscImageCreator.exe")]
        else:
            self.statusBar.showMessage("DiscImageCreator.exe not found!")
            return None

        if self.get_disc_type() is not None:
            command.append(str(self.get_disc_type()))
        else:
            return None

        if self.get_drive_letter() is not None:
            command.append(str(self.get_drive_letter()))

        if self.get_file_name() is not None and self.get_output_directory() is not None:
            command.append(path.normpath(path.abspath(path.join(self.get_output_directory(), self.get_file_name()))))
        else:
            return None

        if self.get_drive_speed() is not None:
            command.append(str(self.get_drive_speed()))
        else:
            return None

        if self.get_options() is not None:
            command.extend(self.get_options())

        return command

    def disable_enable_input(self, state=True):
        self.outputFileName.setEnabled(state)
        self.outputDirectory.setEnabled(state)
        self.browseOutputDir.setEnabled(state)
        self.discType.setEnabled(state)
        self.driveLetter.setEnabled(state)
        self.rb_speed4.setEnabled(state)
        self.rb_speed8.setEnabled(state)
        self.rb_speed16.setEnabled(state)
        self.rb_speed48.setEnabled(state)
        self.rb_speedcustom.setEnabled(state)
        self.customDriveSpeed.setEnabled(state)
        self.zipFiles.setEnabled(state)

    def run_dic(self):
        self.statusBar.showMessage("")
        self.console.setPlainText("")

        if self.create_commandline() is not None:
            print('run')
            self.disable_enable_input(False)
            p = subprocess.Popen(self.create_commandline(),
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)

            for line in iter(p.stdout.readline, ''):
                self.console.appendPlainText(line.decode('UTF-8')[0:-2])
            p.stdout.close()

            #while p.poll() is None:
            #    self.console.appendPlainText(p.st#dout.readline().decode('UTF-8')[0:-2])
            #self.console.appendPlainText(p.stdout.read().decode('UTF-8')[0:-2])

        if self.zipFiles.isChecked() and p.returncode == 0:
            print('zipFiles')

        #self.disable_enable_input(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DicGui()
    window.show()
    sys.exit(app.exec_())