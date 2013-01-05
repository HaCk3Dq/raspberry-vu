#!/usr/bin/env python

import curses
import time
import impulse
import wiringPy

def bar(window, x, y, height, value):
    stop = value * height
    for i in range(height, -1, -1):
        if i < stop:
            label = "****"
            color = (i * 4 / height) + 1
        else:
            label = "    "
            color = 0
        window.addstr(y + height - i, x, label, curses.color_pair(color))

def draw(window):
    h,w = window.getmaxyx()
    audio_sample_array = impulse.getSnapshot(True)
    i = 0
    l = len(audio_sample_array) / 4
    sum = 0
    step = l / ((w - 10) / 5)
    for x in range(3, w - 5, 5):
        value = audio_sample_array[i]
        bar(window, x, 3, h - 6 , value)
        sum += value
        i += step
            
    leds = 8 - min(8, int(sum * 2))
    wiringPy.digital_write_byte((0xFF * (2 ** leds)) & 0xFF)


def main(window):
    wiringPy.setup();
    for pin in range(0,8):
        wiringPy.pin_mode(pin, 1)

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
