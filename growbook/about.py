import gi
from gi.repository import Gtk
import os
import config

(ABOUT_UI,)=(os.path.join(os.path.dirname(__file__),"about.ui"),)

class AboutDialogHandle(object):
    def __init__(self,parent):
        object.__init__(self)
        builder=Gtk.Builder()
        builder.add_from_file(ABOUT_UI)
        builder.connect_signals(self)
        self.dialog=builder.get_object("aboutdialog1")
        self.dialog.set_transient_for(parent)
        self.dialog.handler=self

        self.dialog.set_version('.'.join((str(i) for i in config.config['version'])))
        self.dialog.show_all()
        
    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None

def AboutDialog(parent):
    handler=AboutDialogHandle(parent)
    return handler.dialog

