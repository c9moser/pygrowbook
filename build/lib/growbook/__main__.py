#! /bin/env python

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk
#


import i18n
import app

def main():
    #apphandle=app.AppWindowHandle()
    #window=apphandle.window
    i18n.init()
    window=app.AppWindow()
    window.show_all()
    Gtk.main()
    
    
if __name__ == '__main__':
    main()
