# -*- coding: utf-8 -*-
# growbook/about.py
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
from gi.repository import Gtk
import os
from . import config

(   
    ABOUT_UI,
    LICENSE_FILE
)=(
    os.path.join(os.path.dirname(__file__),"about.ui"),
    os.path.join(os.path.dirname(__file__),"license.txt")
)

class AboutDialogHandle(object):
    def __init__(self,parent):
        object.__init__(self)
        builder=Gtk.Builder()
        builder.add_from_file(ABOUT_UI)
        builder.connect_signals(self)
        self.dialog=builder.get_object("aboutdialog1")
        self.dialog.set_transient_for(parent)
        self.dialog.handler=self
        
        #with open(LICENSE_FILE,'r') as f:
            #self.dialog.set_license(f.read())
        self.dialog.set_version('.'.join((str(i) for i in config.config['version'])))
        self.dialog.show_all()
        
    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None

def AboutDialog(parent):
    handler=AboutDialogHandle(parent)
    return handler.dialog

