#import ..config
import locale
import gettext as _gettext
import os


def init():
    locale.setlocale(locale.LC_ALL,'')
    _gettext.bindtextdomain('growbook',os.path.dirname(__file__))
    _gettext.textdomain('growbook')

gettext=lambda s: _gettext.dgettext('growbook',s)
    
