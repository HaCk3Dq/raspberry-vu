#!/usr/bin/python2

import sys, signal, os, curses, time, impulse, math, subprocess
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

def getDefaultConfig():
  default = {}
  resolution   = subprocess.check_output("xrandr|grep '*'", shell=True).split("   ")[1].split("x")
  screenWidth  = resolution[0]
  screenHeight = int(resolution[1])

  offset = "4" if screenWidth == "1366" else "0"

  default["width"] = screenWidth
  default["height"] = screenHeight/2
  default["xOffset"] = offset
  default["yOffset"] = screenHeight/2
  default["scale"] = 1
  default["color"] = "#ffffff"
  default["transparent"] = "50%"
  default["source"] = 0

  return default

def createConfig(configPath):
  boldGreen   = "\033[32m\x1b[1m"
  resetAttr = "\x1b[0m"
  print "It seems you have started Spectrumyzer for the first time.\nI have generated configuration file for you at the " +\
    boldGreen + configPath + resetAttr

  resolution   = subprocess.check_output("xrandr|grep '*'", shell=True).split("   ")[1].split("x")
  screenWidth  = resolution[0]
  screenHeight = int(resolution[1])

  f = open(configPath,"w")

  default = getDefaultConfig()
  config = ""

  for e in default:
    config += str(e) + " = " + str(default[e]) + "\n"

  f.write(config)

  f.close()

def parseConfig(configPath, window):
  global config
  try:
    with open(configPath) as f: conf = f.readlines()
  except: Exit("cannot open config file")
  
  for e in conf:
    value = e[e.find("=")+2:].rstrip("\n")
    try: value = int(value)
    except:
      if value.find("%") != -1: value = percToFloat(value)
      elif value[0] == "#": value = HexToRGB(value)
      elif e.startswith("scale") : value = float(value)
      else: Exit("wrong " + e[:e.find(" = ")] + " config value")
    config[e[:e.find(" = ")]] = value

  window.set_size_request(config["width"], config["height"])
  window.move(config["xOffset"], config["yOffset"])
  return config["width"], config["color"], config["transparent"], config["source"]

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

# ===== Render =====

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
  if impulse.getSnapshot(True)[0] == 0: return
  window.queue_draw()
  return True

def delta(p, r):
  return p+((r-p)/1.3)

def drawFreq(widget, cr):
  global prev, screenWidth, barWidth, padding
  cr.set_source_rgba(rgbaColor[0], rgbaColor[1], rgbaColor[2], transparent)
  audio_sample = impulse.getSnapshot(True)[:128]

  raw = map(lambda a, b: (a+b)/2, audio_sample[::2], audio_sample[1::2])
  raw = map(lambda y: round(-config["height"]*config["scale"]*y), raw)
  if prev == []: prev = raw
  prev = map(lambda p, r: delta(p, r), prev, raw)

  for i, freq in enumerate(prev):
    cr.rectangle(padding*i, config["height"], barWidth, freq)
  cr.fill()

# ===== main =====

if __name__ == "__main__":
  configPath = os.path.expanduser("~/.spectrum.conf")
  config = getDefaultConfig()
  prev = []
  window = Widget()
  screenWidth = 0
  screenHeight = 0

  if not os.path.isfile(configPath): createConfig(configPath)
  screenWidth, rgbaColor, transparent, source = parseConfig(configPath, window)
  impulse.setup(source)
  impulse.start()
  barWidth = math.ceil((screenWidth-320)/64.0)
  padding = barWidth + 5

  signal.signal(signal.SIGINT, signal.SIG_DFL) # make ^C work
  GLib.timeout_add(40, updateWindow, window)
  Gtk.main()
