#-*- coding:utf-8 -*-

from django.utils.translation import gettext_noop as N_,gettext as _

def get_locale():
    return _('en-US')


LANGUAGES = [
    ('en-US',N_('English - United States')),
    ('de', N_('German')),
]

INDEX_TEMPLATES={
    'en-US': 'main/index.html',
    'de': 'main/de.index.html',
}

PROJECT_GROUPS = [
    (
        'site.operator',
        [
            'user.manage',
            'user.staff.manage',
            'user.superuser.manage',
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
    ('breeder.add',['breeder.add']),
    ('breeder.edit',['breeder.edit']),
    ('breeder.delete',['breeder.delete']),
    ('strain.translate',['strain.translate']),
    ('strain.add',['strain.add']),
    ('strain.delete',['strain.delete']),
    (
        'strains.operator', 
        [
            'breeder.add',
            'breeder.edit'
            'breeder.delete',
            'strain.translate',
            'strain.add',
            'strain.edit',
            'strain.delete'
        ],
    ),
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
    'strains.operator',
]

SUPERUSER_GROUPS = [
    'superuser',
]

