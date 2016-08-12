#!/usr/bin/python2

import sys, signal, os, curses, time, impulse
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# ===== Terminal Rendering =====

def init(window):
  curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
  curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
  curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
  curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)
  curses.curs_set(0)
  curses.use_default_colors()
  window.nodelay(True)
  window.clear()
  window.refresh()

def resizeHandler(window):
  global winH, winW;
  h, w = window.getmaxyx()
  if winH != h or winW != w:
    window.clear()
    winH = h
    winW = w

def printBar(window, x, y, height, value):
  for i in range(height, -1, -1):
    if i < value * height:
      color = (i * 4 / height) + 1
      window.addstr(y + height - i, x, "    ", curses.color_pair(color) | curses.A_BOLD | curses.A_REVERSE)
    else:
      window.addstr(y + height - i, x, "    ")

def terminalDraw(window, h, w):
  audio_sample_array = impulse.getSnapshot(True)
  i = 0
  length = len(audio_sample_array) / 4
  step = length / ((w - 10) / 5)
  for x in range(3, w - 5, 5):
    value = audio_sample_array[i]
    printBar(window, x, 3, h - 6 , value)
    i += step

def render(window):
  init(window)
  while window.getch() != 113 and window.getch() != 185:
    resizeHandler(window)
    terminalDraw(window, winH, winW)
    window.refresh()
    time.sleep(0.05)
  window.clear()
  window.refresh()

# ===== Terminal Rendering =====

def HexToRGB(value):
  try:
    lv = len(value)
    byteValues = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return (round(byteValues[0]*(1/255.0),3),
            round(byteValues[1]*(1/255.0),3),
            round(byteValues[2]*(1/255.0),3),)
  except:
    print "Error: wrong hex color"
    exit()

def parseConfig(argList):
  if len(argList) != 10:
    print "Error: invalid amount of arguments"
    exit()
  for e in ("-w", "-h", "-x", "-y", "-c"): argList.remove(e)
  argList[4] = HexToRGB(argList[4])
  print argList
  window.set_size_request(600,400)
  window.move(300,300)

class Widget(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, skip_pager_hint=True, skip_taskbar_hint=True)
    self.set_wmclass("sildesktopwidget","sildesktopwidget")
    self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
    self.set_keep_below(True)
    screen = self.get_screen()
    rgba = screen.get_rgba_visual()
    self.set_visual(rgba)
    self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(1,1,1,1))
    self.drawArea = Gtk.DrawingArea()
    self.drawArea.connect('draw', drawFreq)
    self.add(self.drawArea)
    self.show_all()

def drawFreq(widget, cr):
  cr.set_source_rgba(0,0.15,0.2,1)
  cr.rectangle(50,75,100,100)
  cr.fill()

def updateWindow(window):
  window.queue_draw()
  return True

# ===== main =====

if __name__ == "__main__":
  argList = sys.argv[1:]
  if len(argList) == 0:
    winH = winW = int
    curses.wrapper(render)
  else:
    rgbaColor = [0, 0, 0]
    window = Widget()
    parseConfig(argList)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # make ^C work
    GLib.timeout_add(20, updateWindow, window)
    Gtk.main()
