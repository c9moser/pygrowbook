from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _,gettext_noop as N_

from .managers import UserManager

# Create your models here.

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(_("email address"),unique=True)
    name = models.CharField(_("name"),max_length=32,blank=True,unique=True)
    first_name = models.CharField(_("first name"),max_length=64,default="")
    last_name = models.CharField(_("last name"),max_length=64,default="")
    date_joined = models.DateTimeField(_("date joined"),auto_now_add=True)
    is_active = models.BooleanField(_("active"),default=True)
    is_superuser = models.BooleanField(_("superuser"),default=False)
    is_staff = models.BooleanField(_("staff"),default=False)
    is_banned = models.BooleanField(_("banned"),default=False)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        permissions = [
            ('user|manage',N_('Allowed to manage users')),
            ('forum|operator',N_('Forum operator')),
            ('forum|thread_create',N_('Allowed to create threads in the forum.')),
            ('forum|thread_post',N_('Allowed to post in forums.')),
            ('pm|allow_all',N_('Allowed to post personal messages to any member')),
            ('wiki|operator',N_('Allowed to remove wiki entries and add new sections')),
            ('wiki|edit_all',N_('Allowed to edit all wiki entries')),
            ('wiki|author',N_('Allowed to create wiki-entries and edit them')),
        ]
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return ' '.join((self.first_name,self.last_name))
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.name
            
    def get_short_name(self):
        return self.name
        
