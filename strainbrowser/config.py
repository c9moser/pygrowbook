#-*- coding:utf-8 -*-
import lzma
import bz2
import gzip

from django.utils.translation import gettext_noop as N_

COMPRESSION = {
    'none': {
        'name': N_('No Compression'),
        'open-func': open,
        'kwargs-write': {
            'mode': 'w'
        },
        'kwargs-read': {
            'mode': 'r'
        },
        'binfmt':False,
    },
    'xz': {
        'name': N_('XZ'),
        'open-func':lzma.open,
        'kwargs-write': {
            'format':lzma.FORMAT_XZ,
            'mode':'wb',
        },
        'kwargs-read': {
            'format':lzma.FORMAT_XZ,
            'mode':'rb',
        },
        'binfmt': True,
        'extension': 'xz',
    },
    'lzma': {
        'name': N_('LZMA'),
        'open-func': lzma.open,
        'kwargs-write': {
            'format': lzma.FORMAT_ALONE,
            'mode': 'wb',
        },
        'kwargs-read' : {
            'format': lzma.FORMAT_ALONE,
            'mode': 'rb',
        },
        'binfmt': True,
        'extension':'lzma',
    },
    'bz2': {
        'name': N_('bzip2'),
        'open-func': bz2.open,
        'kwargs-write': {
            'mode': 'wb',
            'compresslevel': 9,
        },
        'kwargs-read': {
            'mode': 'rb',
        },
        'binfmt': True,
        'extension': 'bz2',
    },
    'gz': {
        'name': N_('gzip'),
        'open-func': gzip.open,
        'kwargs-write': {
            'mode': 'wb',
            'compresslevel': 9,
        },
        'kwargs-read': {
            'mode': 'rb',
        },
        'binfmt': True,
        'extension': 'gz',
    },
}
