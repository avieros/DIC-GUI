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

from os import path, listdir
import subprocess
import zipfile


def read_disc(gui, disc_profiles):
    gui.statusBar.showMessage("")
    cmd = assemble_commandline(gui, disc_profiles)
    if cmd is not None:
        gui.lock_input(True)
        # TODO - Run pre-dump programs
        p = subprocess.Popen(cmd)#, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # TODO - Print console output
        # TODO - Run post-dump programs
        # zip_logs(cmd[4])
    gui.lock_input(False)


def assemble_commandline(gui, disc_profiles):
    # Check for iscImageCreator
    if path.isfile("Release_ANSI\DiscImageCreator.exe"):
        cmd = [path.abspath("Release_ANSI\DiscImageCreator.exe")]
    else:
        gui.statusBar.showMessage("DiscImageCreator.exe not found!")
        return None

    # Check disc type
    profile = disc_profiles[gui.cb_discType.currentText()]

    dt = profile.disc_type
    if dt:
        cmd.append(dt)
    else:
        return None

    # Check disc drive
    dl = drive_letter(gui)
    if dl is not None:
        cmd.append(str(dl))
    else:
        gui.statusBar.showMessage(gui.no_drives)
        return None

    # Check output path
    fn = file_name(gui)
    dr = directory(gui)
    if fn is not None and dr is not None:
        cmd.append(path.normpath(path.abspath(path.join(dr, fn))))
    else:
        return None

    # Check drive speed
    ds = drive_speed(gui)
    if ds is not None:
        cmd.append(ds)
    else:
        return None

    # Check extra options
    cmd.extend(profile.options)

    return cmd


def file_name(gui):
    if gui.le_fileName.text() != "":
        # TODO - Check for illegal characters
        if not gui.le_fileName.text().endswith('.bin'):
            return gui.le_fileName.text() + '.bin'
        else:
            return gui.le_fileName.text()
    gui.statusBar.showMessage("Output file name is malformed. Aborting!")
    return None


def directory(gui):
    if gui.le_dir.text() != "":
        expanded_path = path.expanduser(gui.le_dir.text())
        if path.isdir(expanded_path):
            return expanded_path
    gui.statusBar.showMessage("Output directory is malformed. Aborting!")
    return None


def drive_letter(gui):
    if gui.cb_driveLetter.currentText() != gui.no_drives:
        # TODO - Split this by colon instead
        return gui.cb_driveLetter.currentText().lower()[0]
    return None


def drive_speed(gui):
    if gui.rb_speed4.isChecked():
        return '4'
    elif gui.rb_speed8.isChecked():
        return '8'
    elif gui.rb_speed16.isChecked():
        return '16'
    elif gui.rb_speed48.isChecked():
        return '48'
    elif gui.rb_custom.isChecked():
        if gui.le_customDriveSpeed.text() != "":
            if gui.le_customDriveSpeed.text().isdigit():
                return gui.le_customDriveSpeed.text()
    gui.statusBar.showMessage("Drive speed is not a number. Aborting!")
    return None


def zip_logs(working_dir):
    extensions = ['.log']  # TODO - Add all types
    output = path.join(working_dir, 'logs.zip')
    all_files = listdir(working_dir)
    log_files = []

    for file in all_files:
        if file.endswith(tuple(extensions)):
            log_files.append(file)
    with zipfile.ZipFile(output, 'w') as logs:
        for file in log_files:
            logs.write(file)
    return output
