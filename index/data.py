#-*- coding:utf-8 -*-

from django.utils.translation import gettext as _

INDEX_TEMPLATES={
    'en-US': 'index/index.html',
    'de': 'index/de.index.html',
}

def get_language_code():
    return _('en-US')

