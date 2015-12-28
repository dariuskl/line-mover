# -*- coding: utf8 -*-
#  Line Mover Plugin
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

	def do_activate(self):
		self.kpe_handler = self.window.connect('key-press-event',
							self.on_key_pressed)

	def do_deactivate(self):
		self.window.disconnect(self.kpe_handler)

	def on_key_pressed(self, widget, event):
		defmod = Gtk.accelerator_get_default_mod_mask() & event.state

		if event.keyval == 0xff52 and defmod == Gdk.ModifierType.CONTROL_MASK:
			self.raise_selection()
		elif event.keyval == 0xff54 and defmod == Gdk.ModifierType.CONTROL_MASK:
			self.lower_selection()
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

	def swap_lines(self, doc, ln_a, ln_b):
		"""
			Swaps two arbitrarily positioned lines in `doc`, identified by their
			line numbers `ln_a` resp. `ln_b`.
		"""

		doc.begin_user_action()

		it_a_beg = doc.get_iter_at_line(ln_a)
		it_a_end = doc.get_iter_at_line(ln_a)
		if it_a_end.forward_line():
			it_a_end.backward_char()
		line_a = doc.get_slice(it_a_beg, it_a_end, True)
		doc.delete(it_a_beg, it_a_end)

		it_b_beg = doc.get_iter_at_line(ln_b)
		it_b_end = doc.get_iter_at_line(ln_b)
		it_b_end.forward_line()
		it_b_end.backward_char()
		line_b = doc.get_slice(it_b_beg, it_b_end, True)
		doc.delete(it_b_beg, it_b_end)

		doc.insert(it_b_beg, line_a)
		it_a_beg = doc.get_iter_at_line(ln_a)
		doc.insert(it_a_beg, line_b)

		doc.end_user_action()

	def raise_selection(self):
		doc = self.window.get_active_document()
		doc.begin_user_action()
		self.store_selection(doc)

		ins = doc.get_iter_at_mark(doc.get_insert())
		sel = doc.get_iter_at_mark(doc.get_selection_bound())
		ins_ln = ins.get_line()
		sel_ln = sel.get_line()

		if ins_ln < sel_ln:
			base_ln = ins_ln
			diff = sel_ln - ins_ln
		else:
			base_ln = sel_ln
			diff = ins_ln - sel_ln

		if base_ln == 0:
			doc.end_user_action()
			return

		for l in range(0, diff + 1):
			self.swap_lines(doc, base_ln + l - 1, base_ln + l)

		self.restore_selection(doc, -1)
		doc.end_user_action()

	def lower_selection(self):
		doc = self.window.get_active_document()
		doc.begin_user_action()
		self.store_selection(doc)

		ins = doc.get_iter_at_mark(doc.get_insert())
		sel = doc.get_iter_at_mark(doc.get_selection_bound())
		ins_ln = ins.get_line()
		sel_ln = sel.get_line()

		if ins_ln < sel_ln:
			base_ln = sel_ln
			diff = sel_ln - ins_ln
		else:
			base_ln = ins_ln
			diff = ins_ln - sel_ln

		if base_ln == doc.get_line_count() - 1:
			doc.end_user_action()
			return

		for l in range(0, diff + 1):
			self.swap_lines(doc, base_ln - l + 1, base_ln - l)

		self.restore_selection(doc, 1)
		doc.end_user_action()

# ex:ts=4:
