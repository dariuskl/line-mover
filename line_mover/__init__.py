# -*- coding: utf8 -*-
#  Line Tools Plugin
#
#  Copyright (C) 2015 Darius Kellermann <darius.kellermann@gmail.com>
#  Copyright (C) 2007 Shaddy Zeineddine <shaddyz@users.sourceforge.net>
#  Copyright (C) 2005 Marcus Lunzenauer <mlunzena@uos.de>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gedit

class LineToolsPlugin(GObject.GObject, Gedit.WindowActivatable):

	__gtype_name__ = "LineToolsPlugin"
	window = GObject.property(type=Gedit.Window)
  
	def __init__(self):
		GObject.GObject.__init__(self)
		self.window = None
		self._ctrl_pressed = False

	def do_activate(self):
		self.kpe_handler = self.window.connect('key-press-event',
							self.on_key_pressed)
		self.kre_handler = self.window.connect('key-release-event',
							self.on_key_released)

	def do_deactivate(self):
		self.window.disconnect(self.kpe_handler)
		self.window.disconnect(self.kre_handler)

	def on_key_pressed(self, widget, event):
		if self._ctrl_pressed:
			if event.keyval == 0xff52:
				self.raise_line()
			elif event.keyval == 0xff54:
				self.lower_line()
			else:
				return False
			return True
		if (event.keyval == 0xffe3):
			self._ctrl_pressed = True
		return False

	def on_key_released(self, widget, event):
		if (event.keyval == 0xffe3):
			self._ctrl_pressed = False
		return False

	def raise_line(self, action = None, param = None):
		doc = self.window.get_active_document()
		doc.begin_user_action()
		itstart = doc.get_iter_at_mark(doc.get_insert())
		itstart.set_line_offset(0);
		itstart.backward_line()
		itend = doc.get_iter_at_mark(doc.get_insert())
		itend.set_line_offset(0);
		line = doc.get_slice(itstart, itend, True)
		doc.delete(itstart, itend)
		itend.forward_line()
		doc.insert(itend, line)
		doc.end_user_action()

	def lower_line(self, action = None, param = None):
		doc = self.window.get_active_document()
		doc.begin_user_action()
		itstart = doc.get_iter_at_mark(doc.get_insert())
		itstart.forward_line()
		itend = doc.get_iter_at_mark(doc.get_insert())
		itend.forward_line()
		itend.forward_line()
		line = doc.get_slice(itstart, itend, True)
		doc.delete(itstart, itend)
		itstart.backward_line()
		doc.insert(itstart, line)
		doc.end_user_action()

# ex:ts=4:
