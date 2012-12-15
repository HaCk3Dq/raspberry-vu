#!/usr/bin/env python

import curses
import traceback
import time
import impulse

def bar(window, x, y, height, value):
    stop = value * height
    for i in range(height, -1, -1):
        if i < stop:
            label = "****"
            color = (i * 4 / height) + 1
        else:
            label = "     "
            color = 0
        window.addstr(y + height - i, x, label, curses.color_pair(color))

def draw(window):
    fft = True
    audio_sample_array = impulse.getSnapshot(fft)
    n_bars = 16
    spacing = 5
    x = 5
    l = len(audio_sample_array) / 4
    for i in range(1, l, l / n_bars):
        value = audio_sample_array[i]
        bar(window, x, 3, 16, value)
        x += spacing

def main(window):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)

    window.clear()
    window.border(0)
    window.addstr(2, 2, "Raspberry Pi VU meter")
    window.refresh()
    while True:
        draw(window)
        time.sleep(0.1)

if __name__ == "__main__":
    curses.wrapper(main)
