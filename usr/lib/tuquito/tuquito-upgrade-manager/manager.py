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

import gtk, pygtk
pygtk.require('2.0')
from xml.dom import minidom
from urllib2 import urlopen
from time import sleep
import commands, socket, gettext, os, sys
socket.setdefaulttimeout(10)

# i18n
gettext.install('tuquito-upgrade-manager', '/usr/share/tuquito/locale')

#sleep(10)

class Manager:
	def __init__(self):
		self.glade = gtk.Builder()
		self.glade.add_from_file('./manager.glade')
		self.window = self.glade.get_object('window')
		self.glade.get_object('title').set_markup('<big><b>Tiene instalado ' + myVersion + '</b></big>')
		self.glade.get_object('subtitle').set_markup('Ya está disponible <b>' + newVersion + '</b>!')
		self.glade.get_object('lup').set_label(_('Comenzar la actualización'))
		self.glade.get_object('ldown').set_label(_('Solo descargar la nueva imagen ISO'))
		self.glade.get_object('lview').set_label(_('Ver las nuevas características en la web'))
		self.glade.get_object('lno').set_label(_('No deseo actualizar mi Tuquito'))
		self.glade.connect_signals(self)
		self.window.show()

	def upgrade(self, widget):
		print "upgrade"

	def download(self, widget):
		print "download"

	def view(self, widget):
		os.system('xdg-open ' + notes + ' &')

	def no(self, widget):
		self.glade.get_object('message').set_markup(_('<big><b>Atención</b></big>'))
		self.glade.get_object('message').format_secondary_markup(_('Si desea actualizar su Tuquito luego, puede dirigirse a:\n<i>Menú»Sistema»Adminisración»Upgrade Manager</i>'))
		self.glade.get_object('message').show()

	def about(self, widget, data=None):
		#os.system('/usr/lib/tuquito/garfio/garfio-about.py &')
		os.system('./upgrade-about.py &')

	def quit(self, widget, data=None):
		gtk.main_quit()
		return True

# Mis datos
myCodename = commands.getoutput('cat /etc/tuquito/info | grep CODENAME').split('=')[1]
myRelease = commands.getoutput('cat /etc/tuquito/info | grep RELEASE').split('=')[1]
myStatus = commands.getoutput('cat /etc/tuquito/info | grep STATUS').split('=')[1]

# Intenta conectarse al servidor
try:
	file = urlopen("http://releases.tuquito.org.ar/releases.xml")
except Exception, detail:
	exit

# Parsea el XML
xmldoc = minidom.parseString(file.read())
releases = xmldoc.getElementsByTagName('tuquito')

# Recorre el archivo
for r in releases:
	try:
		cod = r.childNodes[1].firstChild.data
		rel = r.childNodes[3].firstChild.data
		stat = r.childNodes[5].firstChild.data
	except Exception, detail:
		break

	myVersion = 'Tuquito ' + myRelease + ' - ' + myStatus
	newVersion = 'Tuquito ' + rel + ' - ' + stat

	# Compara versiones
	if cod == myCodename:
		if float(rel) > float(myRelease):
			print myRelease + ' > ' + rel
			Manager()
			gtk.main()
			break
		elif (myStatus == 'alpha' and stat == 'beta' or stat == 'stable') or (myStatus == 'beta' and stat == 'stable'):
			print myStatus + ' > ' + stat
			Manager()
			gtk.main()
			break
