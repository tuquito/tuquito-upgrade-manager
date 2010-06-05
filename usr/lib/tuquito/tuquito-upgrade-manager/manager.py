#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Tuquito Upgrade Manager 0.1
 Copyright (C) 2010
 Author: Mario Colque <mario@tuquito.org.ar>
 Tuquito Team! - www.tuquito.org.ar

 This program is free software; you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation; version 3 of the License.
 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.
 You should have received a copy of the GNU General Public License
 along with this program; if not, write to the Free Software
 Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
"""

from time import sleep
import sys

try:
	arg = sys.argv[1].strip()
except Exception, d:
	arg = False

if arg == '-d':
	sleep(10*60)

import gtk, pygtk
pygtk.require('2.0')
from xml.dom import minidom
from urllib2 import urlopen
import commands, socket, gettext, os, string
socket.setdefaulttimeout(10)

# i18n
gettext.install('tuquito-upgrade-manager', '/usr/share/tuquito/locale')

class Manager:
	def __init__(self):
		self.glade = gtk.Builder()
		self.glade.add_from_file('/usr/lib/tuquito/tuquito-upgrade-manager/manager.glade')
		self.window = self.glade.get_object('window')
		self.glade.get_object('title').set_markup(_('<big><b>You have installed %s</b></big>') % myVersion)
		self.glade.get_object('subtitle').set_markup(_('Already available <b>%s</b>!') % newVersion)
		self.glade.get_object('lup').set_label(_('Start upgrade'))
		self.glade.get_object('ldown').set_label(_('Only download the new ISO image'))
		self.glade.get_object('lview').set_label(_('See the new features on the web'))
		self.glade.get_object('lno').set_label(_("I don't want to upgrade my Tuquito"))
		self.glade.connect_signals(self)

	def noUpdate(self, distro):
		self.glade.get_object('message').set_markup(_('<big><b>Information</b></big>'))
		self.glade.get_object('message').format_secondary_markup(_("You've already installed the latest version of Tuquito.\nDistribution: <b>%s</b>") % distro)
		self.glade.get_object('message').show()

	def upgrade(self, widget):
		os.system('tuquitup &')
		self.quit(self)

	def download(self, widget):
		os.system('xdg-open http://www.tuquito.org.ar/descargas.html &')

	def view(self, widget):
		os.system('xdg-open "' + notes + '" &')

	def no(self, widget):
		os.system('touch ' + homePath + 'norun')
		self.glade.get_object('message').set_markup(_('<big><b>Atention</b></big>'))
		self.glade.get_object('message').format_secondary_markup(_('To update Tuquito then you can go to:\n<i>Menu»System»Administration»Upgrade Manager</i>'))
		self.glade.get_object('message').show()

	def about(self, widget, data=None):
		os.system('/usr/lib/tuquito/tuquito-upgrade-manager/upgrade-about.py &')

	def quit(self, widget, data=None):
		gtk.main_quit()
		return True

homePath = os.getenv('HOME') + '/.tuquito/tuquito-upgrade-manager/'
if not os.path.exists(homePath):
	os.system('mkdir -p ' + homePath)

if arg == '-d':
	if os.path.exists(homePath + 'norun'):
		sys.exit(0)

# Mis datos
myCodename = commands.getoutput('cat /etc/tuquito/info | grep CODENAME').split('=')[1]
myRelease = commands.getoutput('cat /etc/tuquito/info | grep RELEASE').split('=')[1]
myStatus = commands.getoutput('cat /etc/tuquito/info | grep STATUS').split('=')[1]
myEdition = commands.getoutput('cat /etc/tuquito/info | grep EDITION').split('=')[1].replace('"', '')

# Intenta conectarse al servidor y parsear el XML
try:
	file = urlopen("http://releases.tuquito.org.ar/releases.xml")
	xmldoc = minidom.parseString(file.read())
	releases = xmldoc.getElementsByTagName('tuquito')
except Exception, detail:
	sys.exit(1)

# Recorre el archivo
for r in releases:
	try:
		cod = r.childNodes[1].firstChild.data
		rel = r.childNodes[3].firstChild.data
		stat = r.childNodes[5].firstChild.data
		notes = r.childNodes[7].firstChild.data
		edition = r.childNodes[11].firstChild.data
	except Exception, detail:
		sys.exit(1)

	myVersion = 'Tuquito %s (%s)' % (myRelease, myStatus)
	newVersion = 'Tuquito %s (%s)' % (rel, stat)

	# Compara versiones
	if myEdition == edition:
		m = Manager()
		if float(rel) > float(myRelease):
			m.window.show()
		elif (myStatus == 'alpha' and stat == 'beta' or stat == 'stable') or (myStatus == 'beta' and stat == 'stable'):
			m.window.show()
		elif arg != '-d':
			if myStatus != 'stable':
				distro = 'Tuquito %s "%s" (%s) - %s' % (myRelease, myCodename.capitalize(), myStatus, myEdition)
			else:
				distro = 'Tuquito %s "%s" - %s' % (myRelease, myCodename.capitalize(), myEdition)
			m.noUpdate(distro)
		else:
			sys.exit(0)
		break
gtk.main()
