#!/usr/bin/python
#    moinmoin_underlay_rpm_cleanup.py
#
#    Cleans entries in MoinMoin's underlay dir not found in rpm listing.
#
#    Copyright (C) 2009 Georg Lutz <georg AT NOSPAM georglutz DOT de>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import optparse
import os
import sys
import types


UNDERLAY_DIR = os.path.abspath("/usr/share/moin/underlay")
VERSIONSTRING = "0.1dev"

parser = optparse.OptionParser(
        usage="%prog [options]",
        version="%prog " + VERSIONSTRING + os.linesep +
        "Copyright (C) 2010 Georg Lutz <georg AT NOSPAM georglutz DOT de")
parser.add_option("-d", dest="delete",
               default=False, action="store_true",
               help="Actually delete files in filesystem (default False)")

(options, args) = parser.parse_args()

if len(args) != 0:
    parser.print_help()
    sys.exit(2)

if not os.path.isdir(UNDERLAY_DIR):
    print "underlay directory not found, nothing to do"
    sys.exit(1)

try:
    f = os.popen("/bin/rpm -ql moin")
except:
    print "rpm command not found"
    sys.exit(1)

lines = f.readlines()
rc = f.close()
if type(rc) == int and rc != 0:
    print "rpm returned unsuccessfull with exit code %d. Is moin really installed as rpm?" % (rc)
    sys.exit(1)

if len(lines) == 0:
    print "rpm call did not return anything"
    sys.exit(1)


# dictionary as we want to store later if directory entry exists or not
rpmEntries = {}

for line in lines:
    if line.find(UNDERLAY_DIR) == 0:
        key = os.path.normpath(line.strip("\n"))
        if key != UNDERLAY_DIR:
            rpmEntries[key] = False

filesOnlyInFileSystem = []
dirsOnlyInFileSystem = []

# topdown=False guarantees that order in list is right for deleting
# (lowermost directories are delete at first)
for dirpath, dirnames, filenames in os.walk(UNDERLAY_DIR, topdown=False):
    for name in filenames:
        fullName = os.path.normpath(os.path.join(dirpath, name))
        if rpmEntries.has_key(fullName):
            rpmEntries[fullName] = True
        else:
            filesOnlyInFileSystem.append(fullName)
    for name in dirnames:
        fullName = os.path.normpath(os.path.join(dirpath, name))
        if rpmEntries.has_key(fullName):
            rpmEntries[fullName] = True
        else:
            dirsOnlyInFileSystem.append(fullName)

print "Remove the following files:"
print ""
for entry in filesOnlyInFileSystem:
    print entry

print ""
print "Remove the following directories:"
print ""
for entry in dirsOnlyInFileSystem:
    print entry

print ""

print "The following rpm files could not be found in filesystem:"
for key in rpmEntries.keys():
    if rpmEntries[key] == False:
        print key
print ""

if len(filesOnlyInFileSystem) > 0 or len(dirsOnlyInFileSystem) > 0:
    if options.delete:
        print "Deleting files..."
        for entry in filesOnlyInFileSystem:
            try:
                os.unlink(entry)
            except:
                print "Could not delete file " + entry
        for entry in dirsOnlyInFileSystem:
            try:
                os.rmdir(entry)
            except:
                print "Could not delete dir " + entry
    else:
        print "Test mode only. Do not delete."
else:
    print "Nothing to do"
