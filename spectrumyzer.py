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
  print (boldRed + "Error: " + boldWhite + text + resetAttr)
  exit()

def getDefaultConfig():
  default = {}
  display = Gdk.Display.get_default()
  monitor = display.get_primary_monitor() or display.get_monitor(0)
  workarea = monitor.get_workarea()
  default['width'] = workarea.width
  default['height'] = workarea.height / 2
  default['xOffset'] = workarea.x
  default['yOffset'] = workarea.y + (workarea.height - default['height'])

  default["height_mid"] = "70%"
  default["height_low"] = "35%"

  default["barsNumber"] = 64

  default["scale"] = 1
  default["color"] = "#ffffff"
  default["color_mid"] = "#dddddd"
  default["color_low"] = "#bbbbbb"
  default["transparent"] = "50%"
  default["source"] = 0
  default["multicolor"] = "off"

  return default

def createConfig(configPath):
  boldGreen   = "\033[32m\x1b[1m"
  resetAttr = "\x1b[0m"
  print ("It seems you have started Spectrumyzer for the first time.\nI have generated configuration file for you at the " +\
    boldGreen + configPath + resetAttr)

  f = open(configPath,"w")
  default = getDefaultConfig()
  config  = ""
  for e in default: config += str(e) + " = " + str(default[e]) + "\n"
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
      elif e.startswith("multicolor") : value = str(value)
      else: Exit("wrong " + e[:e.find(" = ")] + " config value")
    config[e[:e.find(" = ")]] = value

  window.set_size_request(config["width"], config["height"])
  window.move(config["xOffset"], config["yOffset"])
  return config["width"], config["color"], config["color_low"], config["color_mid"], config["transparent"], config["source"]

def HexToRGB(value):
  value = value.lstrip("#")
  lv = len(value)
  try:
    byteValues = tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
    return (round(byteValues[0]*(1/255.0),3),
            round(byteValues[1]*(1/255.0),3),
            round(byteValues[2]*(1/255.0),3))
  except: Exit("wrong hex color")

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
  global idleDelay
  if impulse.getSnapshot(True)[0] == 0:
    if idleDelay == 10: return True
    else: idleDelay += 1
  else: idleDelay = 0
  window.queue_draw()
  return True

def delta(p, r):
  return p+((r-p)/1.3)

def drawFreq(widget, cr):
  global prev, screenWidth
  audio_sample = impulse.getSnapshot(True)[:config["barsNumber"]*2]

  raw = map(lambda a, b: (a+b)/2, audio_sample[::2], audio_sample[1::2])
  raw = map(lambda y: round(-config["height"]*config["scale"]*y), raw)
  if prev == []: prev = raw
  prev = map(lambda p, r: delta(p, r), prev, raw)

  padding = 5
  barsWidth = screenWidth - padding * (barsNumber - 1)
  baseBarWidth = barsWidth / barsNumber
  biggerBarsNumber = barsWidth % barsNumber
  leftOffset = 0

  if config["multicolor"] == "simple":
      for i, freq in enumerate(prev):
        currentWidth = baseBarWidth + int(biggerBarsNumber > i)
        # Draw bottom part of bar
        cr.set_source_rgba(rgbaColor_low[0], rgbaColor_low[1], rgbaColor_low[2], transparent)
        low_freq = config["height_low"]*freq
        cr.rectangle(leftOffset, config["height"], currentWidth, low_freq)
        cr.fill()
        # Draw middle part of bar
        cr.set_source_rgba(rgbaColor_mid[0], rgbaColor_mid[1], rgbaColor_mid[2], transparent)
        mid_freq = (config["height_mid"]-config["height_low"])*freq
        cr.rectangle(leftOffset, config["height"]+low_freq, currentWidth, mid_freq)
        cr.fill()
        # Draw top part of bar
        cr.set_source_rgba(rgbaColor[0], rgbaColor[1], rgbaColor[2], transparent)
        hight_freq = (1-config["height_mid"])*freq
        cr.rectangle(leftOffset, config["height"]+mid_freq+low_freq, currentWidth, hight_freq)
        cr.fill()
        leftOffset += currentWidth + padding
  elif config["multicolor"] == "flat":
      for i, freq in enumerate(prev):
        bar_low = config["height"]*config["height_low"] # Height of 'color_low' part of bar
        bar_mid = config["height"]*(config["height_mid"]-config["height_low"]) # Height of 'color_mid' part of bar
        currentWidth = baseBarWidth + int(biggerBarsNumber > i)
        if -freq <= bar_low: # Draw bar if 'freq' lower than height of 'color_low' part of bar
          cr.set_source_rgba(rgbaColor_low[0], rgbaColor_low[1], rgbaColor_low[2], transparent)
          cr.rectangle(leftOffset, config["height"], currentWidth, freq)
          cr.fill()
        elif -freq <= bar_mid+bar_low: # If 'freq' is highter than height of 'color_low' but lower than 'color_mid' than draw full 'bar_low' and 'freq' on top of it
          cr.set_source_rgba(rgbaColor_low[0], rgbaColor_low[1], rgbaColor_low[2], transparent)
          cr.rectangle(leftOffset, config["height"], currentWidth, -bar_low)
          cr.fill()
          cr.set_source_rgba(rgbaColor_mid[0], rgbaColor_mid[1], rgbaColor_mid[2], transparent)
          cr.rectangle(leftOffset, config["height"]-bar_low, currentWidth, freq+bar_low)
          cr.fill()
        else: # Everything same here: two full bars and 'freq' on top of them
          cr.set_source_rgba(rgbaColor_low[0], rgbaColor_low[1], rgbaColor_low[2], transparent)
          cr.rectangle(leftOffset, config["height"], currentWidth, -bar_low)
          cr.fill()
          cr.set_source_rgba(rgbaColor_mid[0], rgbaColor_mid[1], rgbaColor_mid[2], transparent)
          cr.rectangle(leftOffset, config["height"]-bar_low, currentWidth, -bar_mid)
          cr.fill()
          cr.set_source_rgba(rgbaColor[0], rgbaColor[1], rgbaColor[2], transparent)
          cr.rectangle(leftOffset, config["height"]-bar_low-bar_mid, currentWidth, freq+bar_low+bar_mid)
          cr.fill()
        leftOffset += currentWidth + padding
  elif config["multicolor"] == "off": # Old method, nothing new
      for i, freq in enumerate(prev):
        currentWidth = baseBarWidth + int(biggerBarsNumber > i)
        cr.set_source_rgba(rgbaColor[0], rgbaColor[1], rgbaColor[2], transparent)
        cr.rectangle(leftOffset, config["height"], currentWidth, freq)
        cr.fill()
        leftOffset += currentWidth + padding
  else: Exit("not valid multicolor option; Valid options are \"simple\", \"flat\" and \"off\"")

# ===== main =====

if __name__ == "__main__":
  configPath = os.path.expanduser("~/.spectrum.conf")
  config = getDefaultConfig()
  prev = []
  window = Widget()
  screenWidth = 0
  screenHeight = 0
  idleDelay = 0

  if not os.path.isfile(configPath): createConfig(configPath)
  screenWidth, rgbaColor, rgbaColor_low, rgbaColor_mid, transparent, source = parseConfig(configPath, window)
  impulse.setup(source)
  impulse.start()

  signal.signal(signal.SIGINT, signal.SIG_DFL) # make ^C work
  GLib.timeout_add(40, updateWindow, window)
  Gtk.main()
