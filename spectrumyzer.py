#!/usr/bin/python2

import sys, signal, os, curses, time, impulse
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# ===== Utils =====

def Exit(text):
  boldRed   = "\033[31m\x1b[1m"
  boldWhite = "\033[39m\x1b[1m"
  resetAttr = "\x1b[0m"
  print boldRed + "Error: " + boldWhite + text + resetAttr
  exit()

def helpScreen():
  print "Usage: spectrumyzer [-t|-d] [-c <path>]\n"
  print "  Render modes:"
  print "    -t   render to terminal"
  print "    -d   render to desktop\n"
  print "  If u choose desktop mode then provide a config path"
  print "  (you can find an example in spectrumyzer/spectrum.conf)"
  print "    -c <path>"

def isRenderToTerminal(argList):
  if len(argList) == 0:
    helpScreen()
    exit()
  elif (argList[0] == "-h"):
    helpScreen()
    exit()
  elif (argList[0] == "-t"): return True
  elif (argList[0] == "-d"): return False
  else:
    helpScreen()
    Exit("unknown command")

def parseConfig(argList, window):
  global rgbaColor, transparent, config
  if len(argList) != 3:
    helpScreen()
    Exit("not enough arguments")
  try:
    with open(argList[2]) as f: conf = f.readlines()
  except: Exit("cannot open config file")
  
  for e in conf:
    value = e[e.find("=")+2:].rstrip("\n")
    try: value = int(value)
    except:
      if value.find("%") != -1: value = percToFloat(value)
      elif value[0] == "#": value = HexToRGB(value)
      else: Exit("wrong " + e[:e.find(" = ")] + " config value")
    config[e[:e.find(" = ")]] = value

  window.set_size_request(config["width"], config["height"])
  window.move(config["xOffset"], config["yOffset"])
  rgbaColor = config["color"]
  transparent = config["transparent"]

def HexToRGB(value):
  value = value.lstrip("#")
  lv = len(value)
  try:
    byteValues = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return (round(byteValues[0]*(1/255.0),3),
            round(byteValues[1]*(1/255.0),3),
            round(byteValues[2]*(1/255.0),3),)
  except:
    Exit("wrong hex color")

def percToFloat(value):
  value = value.rstrip("%")
  try: value = int(value) * .01
  except: Exit("wrong transparent format")
  return value

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

# ===== Desktop Rendering =====

class Widget(Gtk.Window):
  def __init__(self):
    Gtk.Window.__init__(self, skip_pager_hint=True, skip_taskbar_hint=True)
    self.set_wmclass("sildesktopwidget","sildesktopwidget")
    self.set_type_hint(Gdk.WindowTypeHint.DESKTOP)
    self.set_keep_below(True)
    screen = self.get_screen()
    rgba = screen.get_rgba_visual()
    self.set_visual(rgba)
    self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0,0,0,0))
    self.drawArea = Gtk.DrawingArea()
    self.drawArea.connect('draw', drawFreq)
    self.add(self.drawArea)
    self.show_all()

def updateWindow(window):
  window.queue_draw()
  return True

def delta(p, r):
  return p+((r-p)/1.3)

def drawFreq(widget, cr):
  global prev
  cr.set_source_rgba(rgbaColor[0], rgbaColor[1], rgbaColor[2], transparent)
  audio_sample = impulse.getSnapshot(True)[:128]

  raw = map(lambda a, b: (a+b)/2, audio_sample[::2], audio_sample[1::2])
  raw = map(lambda y: round(-config["height"]*y), raw)
  if prev == []: prev = raw
  prev = map(lambda p, r: delta(p, r), prev, raw)

  for i, freq in enumerate(prev):
    cr.rectangle(30*i, config["height"], 25, freq)
  cr.fill()

# ===== main =====

if __name__ == "__main__":
  if isRenderToTerminal(sys.argv[1:]):
    winH = winW = int
    curses.wrapper(render)
  else:
    config = {}
    prev = []
    window = Widget()

    parseConfig(sys.argv[1:], window)
    signal.signal(signal.SIGINT, signal.SIG_DFL) # make ^C work
    GLib.timeout_add(40, updateWindow, window)
    Gtk.main()
