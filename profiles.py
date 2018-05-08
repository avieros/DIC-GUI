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


class GenericDisc:
    def __init__(self, name, disc_type, options):
        self.name = name
        self.disc_type = disc_type
        self.options = options


class PlayStation(GenericDisc):
    @staticmethod
    def after_read_exec():
        print('extra')


disc_profiles = {'Audio CD':                 GenericDisc('Audio CD',                 'cd',  ['/c2']),
                 'Any CD Drive (testing)':   GenericDisc('Generic CD',               'data',  ['0', '1000']),
                 'Sony PlayStation':         PlayStation('Sony PlayStation',         'cd',  ['/c2', '/nl']),
                 'Sony PlayStation 2 (CD)':  GenericDisc('Sony PlayStation 2 (CD)',  'cd',  ['/c2']),
                 'Sony PlayStation 2 (DVD)': GenericDisc('Sony PlayStation 2 (DVD)', 'dvd', [])}
