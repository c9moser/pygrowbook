#-*- coding:utf-8 -*-

from django.utils.translation import gettext_noop as N_,gettext as _
from django.contrib.auth.models import Group


def get_locale():
    return _('en-US')

INDEX_TEMPLATE = {
    'en-US': 'main/index/index.html',
    'de': 'main/index/de.index.html',
}

RESET_PASSWORD_MAIL_TEMPLATE = {
    'en-US': 'main/password/password_reset_mail.txt',
    'de': 'main/password/de.password_reset_mail.txt',
}

LANGUAGES = [
    ('en-US',N_('English - United States')),
    ('de', N_('German')),
]
EXTRA_PERMISSIONS = [
    ('group.manage',N_('Allowed to manage Groups'),Group),
#    ('wiki.operator',N_('Wiki operator')),
#    ('forum.operator',N_('Froum operator')),
]

PROJECT_GROUPS = [
    (
        'site.operator',
        [
            'user.manage',
            'user.staff.manage',
            'user.superuser.manage',
            'group.manage',
        ],
    ),
    (
        'superuser',
        [
            'user.manage',
            'user.staff.manage',
        ],
    ),
    (
        'staff',
        [    
            'user.manage',
        ],
    ),
    ('breeder.add',['strainbrowser.breeder.add']),
    ('breeder.edit',['strainbrowser.breeder.edit']),
    ('breeder.delete',['strainbrowser.breeder.delete']),
    ('strain.translate',['strainbrowser.strain.translate']),
    ('strain.add',['strainbrowser.strain.add']),
    ('strain.edit',['strainbrowser.strain.edit']),
    ('strain.delete',['strainbrowser.strain.delete']),
    (
        'strainbrowser.operator', 
        [
            'strainbrowser.operator',
            'strainbrowser.breeder.add',
            'strainbrowser.breeder.edit'
            'strainbrowser.breeder.delete',
            'strainbrowser.strain.translate',
            'strainbrowser.strain.add',
            'strainbrowser.strain.edit',
            'strainbrowser.strain.delete'
        ],
    ),
    #('forum.operator',['forum.operator']),
    #('wiki.operator',['wiki.operator']),
]    

MEMBER_GROUPS = [
    'breeder.add',
    'strain.add',
    'strain.translate',
]

USER_GROUPS_FORMAT = [
    ('user.{uid}.friend',True),
    ('user.{uid}.pm.block',False),
    ('user.{uid}.block',False),
]

STAFF_GROUPS = [
    'staff',
    'strainbrowser.operator',
    #'forum.operator',
    #'wiki.operator',
]

SUPERUSER_GROUPS = [
    'superuser',
]

SITE_OPERATOR_GROUPS = [
    'site.operator',
]

