
import gi
from gi.repository import GLib
import os

config={
    'version':(0,0,20),
    'datadir':os.path.join(GLib.get_user_data_dir(),'growbook'),
    'dbfile':os.path.join(GLib.get_user_data_dir(),'growbook','growbook.db'),
    'open-ongoing-growlogs':True
}

