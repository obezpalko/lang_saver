#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" save language per window
"""

from time import sleep
from xkbgroup import XKeyboard
from Xlib.display import Display

WINDOW_HISTORY = {}
DISPLAY = Display()
XKB = XKeyboard()
PREV_WINDOW = 0
PREV_GROUP = XKB.group_num

while True:
    WINDOW = DISPLAY.get_input_focus().focus.id
    if WINDOW != PREV_WINDOW:
        #  window has been changed
        #  need to check if current group match stored
        #  and if not - restore from stored
        if WINDOW in WINDOW_HISTORY:
            XKB.group_num = WINDOW_HISTORY[WINDOW]
        else:
            WINDOW_HISTORY[WINDOW] = XKB.group_num
        PREV_WINDOW = WINDOW
    else:
        # window wans't changed
        # probably group changed
        # check previous group and if not match - update history
        if PREV_GROUP != XKB.group_num:
            WINDOW_HISTORY[WINDOW] = XKB.group_num
            PREV_GROUP = XKB.group_num
    sleep(0.25)
