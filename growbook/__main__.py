#!/bin/env python
# -*- coding: utf-8 -*-
# growbook/__main__.py
################################################################################
# Copyright (C) 2020  Christian Moser                                          #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
################################################################################

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk

import i18n
import app
import growbook

def main():
    i18n.init()
    if not growbook.window:
        growbook.window=app.AppWindow()
        growbook.window.show_all()
        Gtk.main()
    else:
        growbook.window.present()

if __name__ == '__main__':
    main()
