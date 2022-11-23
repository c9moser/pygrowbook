#-*- coding:utf-8 -*-
from django.utils.translation import gettext_noop as N_

from .models import GrowlogVisibility

GROWLOG_VISIBILITY = [
    ('private',N_("Visible only for one self.")),
    ('friend',N_("Visible for ones friends only.")),
    ('member',N_("Visible for members only.")),
    ('public',N_("Visible for everyone.")),
]

def init_app():
    for name,desc in GROWLOG_VISIBILITY:
        try:
            gv = GrowlogVisibility.objects.get(name=name)
            gv.description = desc
            gv.save()
        except GrowlogVisibility.DoesNotExist:
            gv = GrowlogVisibility.objects.create(name=name,description=desc)
# init_app

