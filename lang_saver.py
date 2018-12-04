#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" save language per window
"""

import logging
from logging.handlers import SysLogHandler
from time import sleep
from xkbgroup import XKeyboard
from Xlib.display import Display
import setproctitle
import sys


class LangSaver():
    def __init__(self, *args, **kwargs):
        self.title = kwargs.pop('title', 'lang_saver')
        setproctitle.setproctitle(self.title)
        self.time = kwargs.pop('time', 0.1)
        self.logger = logging.getLogger(self.title)
        handler = SysLogHandler(address='/dev/log')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)
        self.logger.info('starting {} with refresh time: {}'.format(self.title, self.time))
        self.display = kwargs.pop('display', Display())
        self.xkb = kwargs.pop('xkb', XKeyboard())

    def run(self):
        window_history = {}
        prew_window = 0
        prev_group = self.xkb.group_num
        while True:
            window = self.display.get_input_focus().focus.id
            if window != prew_window:
                #  window has been changed
                #  need to check if current group match stored
                #  and if not - restore from stored
                if window in window_history and self.xkb.group_num != window_history[window]:
                    self.xkb.group_num = window_history[window]
                    self.logger.info('restore lang: {} for window: {}'.format( window_history[window], window))
                else:
                    window_history[window] = self.xkb.group_num
                prew_window = window
            else:
                # window wans't changed
                # probably group changed
                # check previous group and if not match - update history
                if prev_group != self.xkb.group_num:
                    window_history[window] = self.xkb.group_num
                    prev_group = self.xkb.group_num
            try:
                sleep(self.time)
            except KeyboardInterrupt:
                sys.exit(0)

if __name__ == '__main__':
    ls = LangSaver()
    ls.run()
