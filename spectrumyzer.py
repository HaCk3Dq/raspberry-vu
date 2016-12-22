#!/usr/bin/python3
# -*- Mode: Python; indent-tabs-mode: t; python-indent: 4; tab-width: 4 -*-

# import os
# import sys
import impulse
import signal

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib


config = dict(
	left_offset = 10,
	right_offset = 10,
	top_offset = 5,
	bottom_offset = 5,
	padding = 5,
	source = 0,
	scale = 1,
	rgba = Gdk.RGBA(1, 0.5, 0.5, 0.5)
)


class AttributeDict(dict):
	def __getattr__(self, attr):
		return self[attr]

	def __setattr__(self, attr, value):
		self[attr] = value


class SilenceChecker:
	def __init__(self, value=0):
		self.value = value

	def __call__(self, value):
		self.value = 0 if value > 0 else self.value + 1
		return self.value > 10


class MainApp:
	def __init__(self):
		self.is_silence = SilenceChecker()
		self.audio_sample = []
		self.previous_sample = []  # this is formatted one so its len may be different from original

		# init window
		# self.window = Gtk.Window(skip_pager_hint=True, skip_taskbar_hint=True)
		# self.window.set_wmclass("sildesktopwidget","sildesktopwidget")
		# self.window.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
		# self.window.set_keep_below(True)
		self.window = Gtk.Window()
		screen = self.window.get_screen()

		# set window transparent
		self.window.set_visual(screen.get_rgba_visual())
		self.window.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 0))

		# init drawing widget
		self.draw_area = Gtk.DrawingArea()
		self.draw_area.connect("draw", self.redraw)
		self.window.add(self.draw_area)

		# semi constants for drawing
		self.bars = AttributeDict()
		self.bars.padding = config["padding"]
		self.bars.number = 64

		# signals
		GLib.timeout_add(33, self.update)
		self.window.connect("delete-event", self.close)
		self.window.connect("check-resize", self.on_resize)

		# show window
		self.window.show_all()

	def on_resize(self, *args):
		self.bars.win_width = self.draw_area.get_allocated_width() - config["right_offset"]
		self.bars.win_height = self.draw_area.get_allocated_height() - config["bottom_offset"]

		total_width = (self.bars.win_width - config["left_offset"]) - self.bars.padding * (self.bars.number - 1)
		self.bars.width = max(int(total_width / self.bars.number), 1)
		self.bars.height = self.bars.win_height - config["top_offset"]
		self.bars.mark = total_width % self.bars.number  # width correnction point

	def update(self):
		self.audio_sample = impulse.getSnapshot(True)[:128]
		if not self.is_silence(self.audio_sample[0]):
			self.draw_area.queue_draw()
		return True

	def redraw(self, widget, cr):
		cr.set_source_rgba(*config["rgba"])

		raw = list(map(lambda a, b: (a + b) / 2, self.audio_sample[::2], self.audio_sample[1::2]))
		if self.previous_sample == []:
			self.previous_sample = raw
		self.previous_sample = list(map(lambda p, r: p + (r - p) / 1.3, self.previous_sample, raw))

		dx = config["left_offset"]
		for i, value in enumerate(self.previous_sample):
			width = self.bars.width + int(i < self.bars.mark)
			height = self.bars.height * min(config["scale"] * value, 1)
			cr.rectangle(dx, self.bars.win_height, width, - height)
			dx += width + self.bars.padding
		cr.fill()

	def close(self, *args):
		Gtk.main_quit()


if __name__ == "__main__":
	impulse.setup(config["source"])
	impulse.start()
	signal.signal(signal.SIGINT, signal.SIG_DFL)  # make ^C work

	MainApp()
	Gtk.main()
	exit()
