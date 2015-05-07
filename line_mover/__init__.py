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
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gedit

class LineMoverPlugin(GObject.GObject, Gedit.WindowActivatable):

	__gtype_name__ = "LineMoverPlugin"
	window = GObject.property(type=Gedit.Window)
  
	def __init__(self):
		GObject.GObject.__init__(self)
		self.window = None
		self._ctrl_pressed = False

	def do_activate(self):
		self.kpe_handler = self.window.connect('key-press-event',
							self.on_key_pressed)

	def do_deactivate(self):
		self.window.disconnect(self.kpe_handler)

	def on_key_pressed(self, widget, event):
		if event.keyval == 0xff52 and event.state == Gdk.ModifierType.CONTROL_MASK:
			self.raise_line()
		elif event.keyval == 0xff54 and event.state == Gdk.ModifierType.CONTROL_MASK:
			self.lower_line()
		else:
			return False
		return True

	def store_selection(self, doc):
		ins = doc.get_iter_at_mark(doc.get_insert())
		sel = doc.get_iter_at_mark(doc.get_selection_bound())
		self._stored_selection = ((
			ins.get_line(),
			ins.get_line_offset()
		),(
			sel.get_line(),
			sel.get_line_offset()
		))

	def restore_selection(self, doc, at = 0):
		insmark = doc.get_insert()
		ins = doc.get_iter_at_line_offset(self._stored_selection[0][0] + at,
				self._stored_selection[0][1])
		selmark = doc.get_selection_bound()
		sel = doc.get_iter_at_line_offset(self._stored_selection[1][0] + at,
				self._stored_selection[1][1])
		doc.move_mark(insmark, ins)
		doc.move_mark(selmark, sel)

	def raise_line(self):
		doc = self.window.get_active_document()
		doc.begin_user_action()
		self.store_selection(doc)

		insmark = doc.get_insert()

		# get previous line without breaks
		pv_beg = doc.get_iter_at_mark(insmark)
		if not pv_beg.backward_line():
			# first line
			doc.end_user_action()
			return
		pv_end = doc.get_iter_at_mark(insmark)
		pv_end.set_line_offset(0)
		pv_end.backward_char()
		pv = doc.get_slice(pv_beg, pv_end, True)
		doc.delete(pv_beg, pv_end)

		# get current line without breaks
		ln_beg = doc.get_iter_at_mark(insmark)
		ln_beg.set_line_offset(0)
		ln_end = doc.get_iter_at_mark(insmark)
		if ln_end.forward_line():
			# only if it is not the last line, because that is lacking a char
			ln_end.backward_char()
		ln = doc.get_slice(ln_beg, ln_end, True)
		doc.delete(ln_beg, ln_end)

		doc.insert(ln_beg, pv)
		ln_beg.backward_line()
		doc.insert(ln_beg, ln)

		self.restore_selection(doc, -1)
		doc.end_user_action()

	def lower_line(self):
		doc = self.window.get_active_document()
		doc.begin_user_action()
		self.store_selection(doc)

		insmark = doc.get_insert()

		# get next line without breaks
		nx_beg = doc.get_iter_at_mark(insmark)
		if not nx_beg.forward_line():
			# last line
			doc.end_user_action()
			return
		nx_end = doc.get_iter_at_mark(insmark)
		nx_end.forward_line()
		if nx_end.forward_line():
			nx_end.backward_char()
		nx = doc.get_slice(nx_beg, nx_end, True)
		doc.delete(nx_beg, nx_end)

		# get current line without breaks
		ln_beg = doc.get_iter_at_mark(insmark)
		ln_beg.set_line_offset(0)
		ln_end = doc.get_iter_at_mark(insmark)
		ln_end.forward_line()
		ln_end.backward_char()
		ln = doc.get_slice(ln_beg, ln_end, True)
		doc.delete(ln_beg, ln_end)

		doc.insert(ln_beg, nx)
		ln_beg.forward_line()
		doc.insert(ln_beg, ln)

		self.restore_selection(doc, 1)
		doc.end_user_action()

# ex:ts=4:
