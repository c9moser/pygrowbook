from django.db import models
from django.contrib.auth.models import PermissionsMixin,Group
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _,gettext_noop as N_
from django.core.validators import validate_email
from .managers import UserManager
from . import config

class Language(models.Model):
    locale = models.CharField(max_length=16)
    name = models.CharField(max_length=64)
    
    @staticmethod
    def update():
        for locale,name in config.LANGUAGES:
            try:
                lang = Language.objects.get(locale=locale)
                lang.name = name
                lang.save()
            except Language.DoesNotExist:
                Language.objects.create(locale=locale,name=name)
    # Language.update()
    
    def __str__(self):
        return self.locale
# Language class


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(_("email address"),unique=True,validators=[validate_email])
    name = models.CharField(_("name"),max_length=32,blank=True,unique=True)
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
            ('user.manage',N_('Allowed to manage users')),
            ('user.staff.manage',N_('Allowed to add/remove staff-members')),
            ('user.superuser.manage',N_('Allowed to add/remove superusers')),
            ('group.manage',N_('Allowed to manage groups')),
        ]
    # Meta class
    
    def _get_group(self,group):
        if isinstance(group,Group):
            return group
        elif isinstance(group,int):
            try:
                return Group.objects.get(pk=group)
            except Group.DoesNotExist:
                pass
        elif isinstance(group,str):
            try:
                return Group.objects.get(name=group)
            except Group.DoesNotExist:
                pass
        else:
            raise ValueError('group is not a int, str or django.contrib.auth.models.Group instance!')
        return None
    # User._get_group()

    def get_full_name(self):
        return self.name
            
    def get_short_name(self):
        return self.name
        
    def is_in_group(self,group):
        g = self._get_group(group)
        try:
            self.groups.get(name=g.name)
            return True
        except Group.DoesNotExist:
            pass
        return False
    # User.is_in_group()
    
    def add_to_group(self,group):
        g = self._get_group(group)
        if g:
            self.groups.add(g)
        return False
    # User.add_to_group()
        
    def remove_from_group(self,group):
        g = self._get_group(group)
        if g:
            user.groups.remove(g)
    # User.remove_from_group()
        
    def _create_profile(self):
        try:
            profile = UserProfile.objects.get(user=self.id)
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=self)

        profile_languages = (l.locale for l in profile.languages.all())
        lang = config.get_locale()
        if lang != 'en-US' and not lang in profile_languages:
            try: 
                language = Language.objects.get(locale=lang)
                profile.languages.add(language)
            except Language.DoesNotExist:
                pass
                
        if 'en-US' not in profile_languages:
            language = Language.objects.get(locale='en-US')
            profile.languages.add(language)
    # User._create_profile()
        
    def add_to_user_groups(self):
        for group_name_fmt,add_to_group in config.USER_GROUPS_FORMAT:
            group_name = group_name_fmt.format(uid=self.id)
            group = self._get_group(group_name)
            if not group:
                Group.objects.create(name=group_name)
            if add_to_group:
                self.groups.add(group)
    # User.add_to_user_groups
        
    def make_member(self):
        self.is_banned = False
        self.save()
        
        self.add_to_user_groups()
        
        for group_name in config.MEMBER_GROUPS:
            if not self.is_in_group(group_name):
                self.add_to_group(group_name)
            
        self._create_profile()
    # User.make_user()
        
    def make_ban(self): 
        self.is_banned = True
        self.is_staff = False
        self.is_superuser = False
        self.save()
        
        for group in self.groups.all():
            if not group.name.startswith('user.'):
                self.groups.remove(group)
    # User.make_ban()
    
    def make_staff_member(self):
        self.make_member()
        
        self.is_staff = True
        self.save()
        
        for group_name in config.STAFF_GROUPS:
            if not self.is_in_group(group_name):
                self.add_to_group(group_name)
    # User.make_staff_member()
        
    def remove_staff_member(self):
        if self.is_superuser:
            self.remove_superuser()
            
        if self.is_staff:
            self.is_staff = False
            self.save()
            for group_name in config.STAFF_GROUPS:
                if self.is_in_group(group_name):
                    self.remove_from_group(group_name)
    # User.remove_staff_member()
        
    def make_superuser(self):
        if not self.is_staff:
            self.make_staff_member()
        self.is_superuser = True
        self.save()
        
        for group_name in config.STAFF_GROUPS:
            if not self.is_in_group(group_name):
                self.add_to_group(group_name)
    # User.make_superuser()
        
    def remove_superuser(self):
        if self.is_superuser:
            self.is_superuser = False
            self.save()
            
            for group_name in config.SUPERUSER_GROUPS:
                if self.is_in_group(group_name):
                    self.remove_from_group(group_name)
    # User.remove_superuser()
# User class

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    avatar = models.ImageField(null=True,upload_to='avatars/')
    languages = models.ManyToManyField(Language)

