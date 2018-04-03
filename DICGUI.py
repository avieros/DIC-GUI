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

import sys
from PyQt5 import QtWidgets, uic
from os import path
from collections import namedtuple, OrderedDict


qtCreatorFile = "mainwindow.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class DicGui(QtWidgets.QMainWindow, Ui_MainWindow):
    disc_profiles = {}

    profile = namedtuple("Profile", "disc_type extra_options")

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # TODO - Read these from JSON or something more modular
        profiles = {"Sony PlayStation": self.profile('cd', ['/c2', '/nl']),
                    "Sony PlayStation 2 (CD)": self.profile('cd', ['/c2']),
                    "Sony PlayStation 2 (DVD)": self.profile('dvd', [])}

        self.disc_profiles = OrderedDict(sorted(profiles.items(), key=lambda t: t[0]))

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
        return None

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
        # TODO - Check that DIC is found
        command = ["DiscImageCreator"]

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

    def run_dic(self):
        self.statusBar.showMessage("")

        if self.create_commandline() is not None:
            print(self.create_commandline())

        if self.zipFiles.isChecked():
            print('zipFiles')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = DicGui()
    window.show()
    sys.exit(app.exec_())