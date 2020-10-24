#! /bin/env python

try:
    import gi; gi.require_version('Gtk','3.0')
except:
    raise Exception('PyGtk not installed!')
    
from distutils.core import setup
from growbook import config

setup(name='GrowBook',
      version='.'.join((str(i) for i in config.config['version'])),
      description='A logging utility for homegrowers.',
      author='Christian Moser',
      packages=['growbook',
                'growbook.i18n',
                'growbook.i18n.de',
                'growbook.i18n.de.LC_MESSAGES'],
      package_dir={'growbook':'growbook','growbook.i18n':'growbook/i18n'},
      package_data={'growbook':['*.ui','*.sql','*.svg'],
                    'growbook.i18n': ['*.pot','*.po'],
                    'growbook.i18n.de.LC_MESSAGES': ['*.mo','*.po']})
    

