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
	width = 1920,
	height = 1080 / 2,
	xOffset = 0,
	yOffset = 540,
	source = 0,
	scale = 1,
	rgba = Gdk.RGBA(1, 0.5, 0.5, 0.5)
)


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
		self.padding = 5
		self.bars_number = 64
		total_bars_width = config["width"] - self.padding * (self.bars_number - 1)
		self.base_bar_width = int(total_bars_width / self.bars_number)
		self.bar_step = (self.base_bar_width + self.padding)
		self.left_offset = (total_bars_width - self.base_bar_width * self.bars_number) / 2

		# signals
		GLib.timeout_add(40, self.update)
		self.window.connect("delete-event", self.close)

		# show window
		self.window.show_all()

	def update(self):
		self.audio_sample = impulse.getSnapshot(True)[:128]
		if not self.is_silence(self.audio_sample[0]):
			self.draw_area.queue_draw()
		return True

	def redraw(self, widget, cr):
		cr.set_source_rgba(*config["rgba"])

		raw = map(lambda a, b: (a + b) / 2, self.audio_sample[::2], self.audio_sample[1::2])
		raw = list(map(lambda y: round(-config["height"] * config["scale"] * y), raw))
		if self.previous_sample == []:
			self.previous_sample = raw
		self.previous_sample = list(map(lambda p, r: p + (r - p) / 1.3, self.previous_sample, raw))

		for i, value in enumerate(self.previous_sample):
			cr.rectangle(self.left_offset + i * self.bar_step, config["height"], self.base_bar_width, value)
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
