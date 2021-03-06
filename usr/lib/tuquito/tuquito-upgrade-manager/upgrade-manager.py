#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 Tuquito Upgrade Manager 0.3
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

import gtk
from time import sleep
from xml.dom import minidom
from urllib2 import urlopen
import commands, socket, gettext, os, string, sys
socket.setdefaulttimeout(10)
import threading

# i18n
gettext.install('tuquito-upgrade-manager', '/usr/share/tuquito/locale')
gtk.gdk.threads_init()

class MessageDialog:
	def __init__(self, title, message, style):
		self.title = title
		self.message = message
		self.style = style

	def show(self):
		dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, self.style, gtk.BUTTONS_OK, self.message)
		dialog.set_icon_from_file('/usr/lib/tuquito/tuquito-upgrade-manager/logo.png')
		dialog.set_title(_('Upgrade Tuquito'))
		dialog.set_position(gtk.WIN_POS_CENTER)
	        dialog.run()
	        dialog.destroy()

class UpgradeThread(threading.Thread):
	def __init__(self, socketId, glade):
		threading.Thread.__init__(self)
		self.socketId = socketId
		self.glade = glade

	def run(self):
		try:
			gtk.gdk.threads_enter()
			self.glade.get_object('window').hide()
			gtk.gdk.threads_leave()
			os.system('gksu "synaptic --non-interactive --hide-main-window --update-at-startup --parent-window-id ' + self.socketId + '" -D /usr/share/applications/tuquito-upgrade-manager.desktop')
			os.system('gksu "synaptic --non-interactive --hide-main-window --set-selections-file /usr/lib/tuquito/tuquito-upgrade-manager/tuquitup.list --parent-window-id ' + self.socketId + '" -D /usr/share/applications/tuquito-upgrade-manager.desktop')
			os.system('gksu /usr/lib/tuquito/tuquitup/tuquitup &')
			gtk.main_quit()
		except Exception, detail:
			message = MessageDialog('Error', _('An error occurred during the upgrade: ') + str(detail), gtk.MESSAGE_ERROR)
	    		message.show()

class Manager:
	def __init__(self):
		self.glade = gtk.Builder()
		self.glade.add_from_file('/usr/lib/tuquito/tuquito-upgrade-manager/upgrade-manager.glade')
		self.window = self.glade.get_object('window')
		self.window.set_title(_('Upgrade Tuquito'))
		self.glade.get_object('title').set_markup(_('<big><b>You have installed %s</b></big>') % myVersion)
		self.glade.get_object('subtitle').set_markup(_('Already available <b>%s</b>!') % newVersion)
		self.glade.get_object('lup').set_label(_('Start upgrade'))
		self.glade.get_object('ldown').set_label(_('Only download the new ISO image'))
		self.glade.get_object('lview').set_label(_('See the new features on the web'))
		self.glade.get_object('lno').set_label(_("I don't want to upgrade my Tuquito"))
		self.glade.connect_signals(self)

	def noUpdate(self, distro):
		self.glade.get_object('message').set_title(_('Upgrade Tuquito'))
		self.glade.get_object('message').set_markup(_('<big><b>Information</b></big>'))
		self.glade.get_object('message').format_secondary_markup(_("You've already installed the latest version of Tuquito.\nDistribution: <b>%s</b>") % distro)
		self.glade.get_object('message').show()

	def upgrade(self, widget):
		self.vbox = self.glade.get_object('vbox1')
		# Obtiene el socket de la ventana para synaptic
		socket = gtk.Socket()
		self.vbox.pack_start(socket)
		socket.show()
		self.socketId = repr(socket.get_id())
		# Inicia la actualización
		upgrade = UpgradeThread(self.socketId, self.glade)
		upgrade.start()

	def download(self, widget):
		os.system('xdg-open http://www.tuquito.org.ar/descargas.html &')

	def view(self, widget):
		global notes
		os.system('xdg-open "' + notes + '" &')

	def no(self, widget):
		os.system('touch ' + os.path.join(homePath, 'norun'))
		self.glade.get_object('message').set_markup(_('<big><b>Atention</b></big>'))
		self.glade.get_object('message').format_secondary_markup('%s:\n<i>%s»%s»%s»%s</i>' % (_('To update Tuquito later, you can go to'), _('Menu'), _('System'), _('Administration'), _('Tuquito Upgrade Manager')))
		self.glade.get_object('message').show()

	def about(self, widget):
		abt = self.glade.get_object('about')
		abt.connect('response', self.quitAbout)
		abt.connect('delete-event', self.quitAbout)
		abt.connect('destroy-event', self.quitAbout)
		abt.set_comments(_('Upgrade Manager for Tuquito'))
		abt.show()

	def quitAbout(self, widget, data=None):
		widget.hide()
		return True

	def quit(self, widget, data=None):
		gtk.main_quit()
		return True

class ConectThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.glade = gtk.Builder()
		self.glade.add_from_file('/usr/lib/tuquito/tuquito-upgrade-manager/upgrade-manager.glade')
		self.window = self.glade.get_object('loading')
		self.glade.get_object('loading_label').set_text(_('Connecting to server...'))

	def quit(self, widget, data=None):
		gtk.main_quit()
		return True

	def run(self):
		global myVersion, newVersion, notes
		try:
			releases = ''
			if arg != '-d':
				gtk.gdk.threads_enter()
				self.window.show_all()
				gtk.gdk.threads_leave()
			file = urlopen("http://releases.tuquito.org.ar/releases.xml")
			xmldoc = minidom.parseString(file.read())
			releases = xmldoc.getElementsByTagName('tuquito')
			gtk.gdk.threads_enter()
			self.window.hide()
			gtk.gdk.threads_leave()
		except:
			if arg != '-d':
				gtk.gdk.threads_enter()
				self.window.hide()
				message = MessageDialog('Error', _('Error connecting to server.\nTry again later.'), gtk.MESSAGE_ERROR)
				message.show()
				gtk.gdk.threads_leave()
			self.quit(self)

		# Recorre el archivo
		for r in releases:
			try:
				cod = r.childNodes[1].firstChild.data
				rel = r.childNodes[3].firstChild.data
				stat = r.childNodes[5].firstChild.data
				notes = r.childNodes[7].firstChild.data
				edition = r.childNodes[11].firstChild.data
			except:
				sys.exit(1)

			myVersion = 'Tuquito %s (%s)' % (myRelease, myStatus)
			newVersion = 'Tuquito %s (%s)' % (rel, stat)

			# Compare versions
			if myEdition == edition:
				m = Manager()
				if (float(rel) > float(myRelease)) or (myStatus == 'alpha' and (stat == 'beta' or stat == 'rc' or stat == 'stable')) or (myStatus == 'beta' and (stat == 'rc' or stat == 'stable')) or (myStatus == 'rc' and stat == 'stable'):
					m.window.show()
				elif arg != '-d':
					if myStatus != 'stable':
						distro = 'Tuquito %s "%s" (%s) - %s' % (myRelease, myCodename.capitalize(), myStatus, myEdition)
					else:
						distro = 'Tuquito %s "%s" - %s' % (myRelease, myCodename.capitalize(), myEdition)
					m.noUpdate(distro)
				else:
					gtk.main_quit()
				break

# Init
try:
	arg = sys.argv[1].strip()
except:
	arg = False

homePath = os.path.join(os.getenv('HOME'), '.tuquito/tuquito-upgrade-manager')
if not os.path.exists(homePath):
	os.system('mkdir -p %s &' % homePath)

# My data
try:
	myCodename = commands.getoutput('grep CODENAME /etc/tuquito/info').split('=')[1]
	myRelease = commands.getoutput('grep RELEASE /etc/tuquito/info').split('=')[1]
	myStatus = commands.getoutput('grep STATUS /etc/tuquito/info').split('=')[1]
	myEdition = commands.getoutput('grep EDITION /etc/tuquito/info').split('=')[1].replace('"', '')
except Exception, details:
	message = MessageDialog('Error', _('An error occurred during connection: ') + str(detail), gtk.MESSAGE_ERROR)
	message.show()
	sys.exit(1)

# Threads
conect = ConectThread()
conect.start()
gtk.main()
