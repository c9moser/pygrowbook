# -*- coding: utf-8 -*-
# growbook/i18n/__init__.py
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

import locale
import gettext as _gettext
import os


def init():
    locale.setlocale(locale.LC_ALL,'')
    _gettext.bindtextdomain('growbook',os.path.dirname(__file__))
    _gettext.textdomain('growbook')

gettext=lambda s: _gettext.dgettext('growbook',s)
    
