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
from PyQt5.QtGui import QTextCursor
import subprocess
import fnmatch
import zipfile
import requests
import zlib
from bs4 import BeautifulSoup




def read_disc(gui, disc_profiles, app):
    gui.statusBar.showMessage("")
    cmd = assemble_commandline(gui, disc_profiles)
    if cmd is not None:
        gui.lock_input(True)
        gui.pt_console.clear()
        app.processEvents()
        # TODO - Run pre-dump programs
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        buf = bytearray()
        while True:
            c = p.stdout.read(1)
            if c == b"" and p.poll() is not None:
                break
            if c == b"\r":
                n = p.stdout.read(1)
                if n == b"\n":
                    gui.pt_console.appendPlainText(str(buf.decode('UTF-8')))
                    app.processEvents()
                    buf = bytearray()
                else:
                    cursor = gui.pt_console.textCursor()
                    cursor.select(QTextCursor.LineUnderCursor)
                    cursor.removeSelectedText()
                    gui.pt_console.insertPlainText(str(buf.decode('UTF-8')))
                    app.processEvents()
                    buf = bytearray()
                    buf += n
            else:
                buf += c
        if p.returncode != 0:
            gui.statusBar.showMessage("Reading image failed! Please read DIC output.")
        # TODO - Run post-dump programs
        # this next bit only works if single track - need some code here to find out if FILENAME.BIN or FILENAME (Track 01).bin
        for file in os.listdir(directory(gui)):
        if fnmatch.fnmatch(file, '*Track 02*.bin'):
        crcFileName = gui.le_fileName.text() + ' Track 01' + '.bin'
        else crcFileName = gui.le_fileName.text() + '.bin'
        
        buffersize = 65536
        with open(crcFileName, 'rb') as afile:
            buffr = afile.read(buffersize)
            crcvalue = 0
        while len(buffr) > 0:
                crcvalue = zlib.crc32(buffr, crcvalue)
                buffr = afile.read(buffersize)
        crc = (format(crcvalue & 0xFFFFFFFF, '08x'))
        #print (crc)
        url1 = "http://redump.org/discs/quicksearch/"
        r = requests.get(url1 + crc)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'html.parser')
        soup2 = soup.find_all('title')
        soup3 = [e.get_text() for e in soup2]
        if str('Discs') in str(soup3):
            gui.statusBar.showMessage("This disc is a new entry to Redump DB!")
        else:
            gui.statusBar.showMessage("This disc can be used to verify a Redump DB entry")
        # get crc of filename
        if gui.zipFiles.isChecked() and p.returncode == 0:
           zip_logs(path.dirname(cmd[3]))
        gui.lock_input(False)


def assemble_commandline(gui, disc_profiles):
    # Check for DiscImageCreator
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
    gui.statusBar.showMessage("Output file name not set. Aborting!")
    return None


def directory(gui):
    if gui.le_dir.text() != "":
        expanded_path = path.expanduser(gui.le_dir.text())
        if path.isdir(expanded_path):
            return expanded_path
    gui.statusBar.showMessage("Output directory not set. Aborting!")
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
    extensions = ['.c2', '.ccd', '.cue', '.dat', '.sub', '.txt']  # TODO - Add all types
    output = path.join(working_dir, 'logs.zip')
    all_files = listdir(working_dir)
    log_files = []

    for file in all_files:
        if file.endswith(tuple(extensions)):
            log_files.append(file)
    logs = zipfile.ZipFile(output, compression=zipfile.ZIP_DEFLATED, mode='w')
    if log_files:
        for file in log_files:
            logs.write(path.join(working_dir, file), arcname=file)
        logs.close()
    return output
