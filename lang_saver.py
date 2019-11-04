#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" save language per window in sway/i3
"""

import logging
import os
import setproctitle
import sys
import i3ipc
from systemd.journal import JournaldLogHandler

encodings = ['English (US, intl., with dead keys)', 'Hebrew', 'Ukrainian']
xkb_layouts = ['us(intl)', 'il', 'ua(unicode)']
window_layouts = {}


def get_layout(encoding):
    global encodings, xkb_layouts
    if encoding in encodings:
        return xkb_layouts[encodings.index(encoding)]
    else:
        return 'us(intl)'


def main():
    setproctitle.setproctitle(os.path.basename(sys.argv[0]))
    i3 = i3ipc.Connection()
    log = logging.getLogger(os.path.basename(sys.argv[0]))
    journald_handler = JournaldLogHandler()
    # journald_handler.setFormatter(logging.Formatter(
    #     '[%(levelname)s] %(message)s'
    # ))
    log.addHandler(journald_handler)
    log.setLevel(logging.DEBUG)
    pid_file = f'/run/user/{os.getuid()}/{os.path.basename(sys.argv[0])}.pid'
    if os.path.exists(pid_file):
        log.critical(f'pid file exists {pid_file}')
        print(f'pid file exists {pid_file}')
        sys.exit()
    f = open(pid_file, 'w')
    f.write(f'{os.getpid()}')
    f.close()

    def get_input() -> i3ipc.InputReply:
        for input_object in i3.get_inputs():
            if input_object.identifier == '1:1:AT_Translated_Set_2_keyboard':
                # TODO: get keyboard from cmd arguments
                return input_object

    def on_input(self: i3ipc.Connection, ev: i3ipc.InputEvent):
        global window_layouts
        focused_window = i3.get_tree().find_focused()
        if focused_window.id:
            window_layouts[focused_window.id] = ev.input
            log.info(
                f'store window: {focused_window.id} {ev.change} {ev.input.xkb_active_layout_name} {ev.input.xkb_layout_names}')

    def on_focus(self: i3ipc.Connection, ev: i3ipc.WindowEvent):
        global window_layouts
        stored_input = None
        try:
            stored_input = window_layouts[ev.container.id]
        except KeyError:
            log.info(f'no input stored for window {ev.container.id}')
            current_input = get_input()
            window_layouts[ev.container.id] = current_input
            log.info(
                f'store window: {ev.container.id} xkb_layout {current_input.xkb_active_layout_name} {current_input.xkb_layout_names}')
            return
        current_input = get_input()
        if current_input.xkb_active_layout_index == stored_input.xkb_active_layout_index and current_input.xkb_layout_names == stored_input.xkb_layout_names:
            log.info(f'window: {ev.container.id}. everything match. no changes required')
            return
        else:
            main_lang = get_layout(stored_input.xkb_active_layout_name)
            second_lang = get_layout(
                list(filter(lambda x: x != stored_input.xkb_active_layout_name, stored_input.xkb_layout_names))[0])
            log.info(
                f'update: input {stored_input.identifier} xkb_layout "{main_lang},{second_lang}"')
            result = i3.command(f'input {stored_input.identifier} xkb_layout "{main_lang},{second_lang}"')
            if result[0].error:
                log.warning(f'error: {result[0].error}')

    # Subscribe to events
    i3.on("window::focus", on_focus)
    i3.on("input::xkb_keymap", on_input)
    i3.on("input::xkb_layout", on_input)
    # Start the main loop and wait for events to come in.
    i3.main()
    os.unlink(pid_file)


if __name__ == '__main__':
    main()
