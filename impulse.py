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
    audio_sample_array = impulse.getSnapshot(True)
    x = 5
    l = len(audio_sample_array) / 4
    for i in range(0, l, l / 16):
        value = audio_sample_array[i]
        bar(window, x, 3, 16, value)
        x += 5

def main(window):
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_RED)
    curses.curs_set(0)

    window.nodelay(True)
    window.clear()
    window.border(0)
    window.addstr(2, 2, "Raspberry Ladder VU meter")
    window.refresh()
    while window.getch() < 0:
        draw(window)
        window.refresh()
        time.sleep(0.05)

    window.clear()
    window.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
