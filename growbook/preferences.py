# -*- coding: utf-8 -*-
# growbook/preferences.py
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

from gi.repository import Gtk
import os
import config

(PREFERENCES_UI,) = (os.path.join(os.path.dirname(__file__),'preferences.ui'),)

class PreferencesDialogHandle(object):
    def __init__(self,parent,dbcon):
        self.dbcon=dbcon
        builder=Gtk.Builder.new_from_file(PREFERENCES_UI)
        builder.connect_signals(self)
        
        self.dialog=builder.get_object('dialog1')
        self.dialog.set_transient_for(parent)
        self.dialog.handler=self
        
        self.dialog.open_ongoing_growlogs_checkbutton=builder.get_object('checkbutton1')
        self.dialog.open_ongoing_growlogs_checkbutton.set_active(config.config['open-ongoing-growlogs'])

    def on_apply_clicked(self,button):
        config.config['open-ongoing-growlogs']=self.dialog.open_ongoing_growlogs_checkbutton.get_active()
        config.save_config(self.dbcon)

    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None
        
def PreferencesDialog(parent,dbcon):
    handler=PreferencesDialogHandle(parent,dbcon)
    return handler.dialog

