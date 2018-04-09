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

from PyQt5 import QtWidgets, uic
from os import path
from profiles import disc_profiles
from read_disc import read_disc
import wmi

qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DicGui(QtWidgets.QMainWindow, Ui_MainWindow):
    no_drives = "No optical drives found"

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.cb_driveLetter.addItems(self.available_drives())
        self.rb_custom.toggled.connect(lambda: self.custom_drive_speed_status(self.rb_custom))
        self.pb_browseDir.clicked.connect(self.browse_directory)
        self.cb_discType.addItems(disc_profiles)
        self.pb_start.clicked.connect(lambda: read_disc(self, disc_profiles, app))
        # TODO - Add cancel button
        # TODO - Add "new disc info" dialog - easily copyable data

    def available_drives(self):
        c = wmi.WMI()
        drives = []
        for drive in c.Win32_CDROMDrive():
            drives.append(str(drive.Drive) + ' [' + str(drive.Caption) + ']')
        if not drives:
            return [self.no_drives]
        return drives

    def custom_drive_speed_status(self, button):
        if button.isChecked():
            self.le_customDriveSpeed.setEnabled(True)
        else:
            self.le_customDriveSpeed.setEnabled(False)

    def browse_directory(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                               'Browse',
                                                               path.expanduser(self.le_dir.text()))
        if directory is not "":
            self.le_dir.setText(directory)

    def lock_input(self, state):
        state = not state
        self.le_fileName.setEnabled(state)
        self.le_dir.setEnabled(state)
        self.pb_browseDir.setEnabled(state)
        self.cb_discType.setEnabled(state)
        self.cb_driveLetter.setEnabled(state)
        self.rb_speed4.setEnabled(state)
        self.rb_speed8.setEnabled(state)
        self.rb_speed16.setEnabled(state)
        self.rb_speed48.setEnabled(state)
        self.rb_custom.setEnabled(state)
        if self.rb_custom.isChecked():
            self.le_customDriveSpeed.setEnabled(state)
        self.zipFiles.setEnabled(state)
        self.pt_console.setEnabled(state)
        self.pb_start.setEnabled(state)
