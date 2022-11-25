from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator,validate_slug
from django.conf import settings
import datetime

from main.models import User
from main.models import Language
from main import config

# Create your models here.

class Breeder(models.Model):
    key = models.CharField(max_length=64,
                           unique=True,
                           validators=[validate_slug])
    name = models.CharField(max_length=128, 
                            unique=True)
    seedfinder = models.CharField(max_length=512,
                                  blank=True,
                                  default="",
                                  validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    homepage = models.CharField(max_length=512,
                                blank=True,
                                default="",
                                validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    added_by = models.ForeignKey(User,
                                 related_name='breeder_added',
                                 null=True,
                                 on_delete=models.SET_NULL)
    added_on = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User,
                                  related_name='breeder_edited',
                                  null=True,
                                  on_delete=models.SET_NULL)
    edited_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        permissions=[
            ('strainbrowser.operator',_('Strainbrowser operator')),
            ('strainbrowser.breeder.add',_("Allowed to add breeders")),
            ('strainbrowser.breeder.edit',_("Allowed to edit all breeders")),
            ('strainbrowser.breeder.delete',_('Allowed to delete breeders')),
        ]

    def __str__(self):
        return self.name
# Breeder class

class Strain(models.Model):
    breeder = models.ForeignKey(Breeder,
                                on_delete=models.RESTRICT,
                                editable=False)
    key = models.CharField(max_length=64,
                           validators=[validate_slug])
    name = models.CharField(max_length=256)
    seedfinder = models.CharField(max_length=512,
                                  blank=True,
                                  default="",
                                  validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    homepage = models.CharField(max_length=512,
                                blank=True,
                                default="",
                                validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    info = models.TextField(default="",
                            blank=True)
    description = models.TextField(default="",
                                   blank=True)
    added_by = models.ForeignKey(User,
                                 editable=False,
                                 related_name='strain_added',
                                 on_delete=models.RESTRICT)
    added_on = models.DateTimeField(auto_now_add=True,
                                    editable=False)
    edited_by = models.ForeignKey(User,
                                  editable=False,
                                  related_name='strain_edited',
                                  on_delete=models.RESTRICT)
    edited_on = models.DateTimeField(auto_now=True,
                                     editable=False)
    
    class Meta:
        permissions=[
            ('strainbrowser.strain.translate',_('Allowed to translate strains')),
            ('strainbrowser.strain.add',_("Allowed to add strains")),
            ('strainbrowser.strain.edit',_("Allowed to edit strains")),
            ('strainbrowser.strain.delete',_("Allowed to delete strains")),
        ]

    def __str__(self):
        return self.name

    def get_growlogs(self,user=None):
        growlog_list = []
        for growlog in self.growlog_set.all().order_by('title'):
            if growlog.is_visible(user):
                growlog_list.append(growlog)   
        return growlog_list
    # Strain.get_growlogs()
    
    @property
    def locale(self):
        locale = config.get_locale()
        if locale != 'en-US':
            try:
                self.straintranslation_set.get(language__name=locale)
                return locale
            except StrainTranslation.DoesNotExist:
                pass
        return 'en-US'
    # Strain.locale
    
    @property
    def locale_translation(self):
        locale = config.get_locale()
        try:
            translation = self.straintranslation_set.get(language__locale=locale)
            return translation
        except StrainTranslation.DoesNotExist:
            pass
        except Exception as error:
            print(error)
        return None
    # Strain.locale_translation
    
    @property
    def locale_description(self):
        translation = self.locale_translation
        if translation and translation.description:
            return translation.description
        return self.description
    # Strain.locale_description
    
    @property
    def locale_info(self):
        translation = self.locale_translation
        if translation and translation.info:
            return translation.info
        return self.info
    # Strain.locale_info
        
    @property
    def locale_seedfinder(self):
        translation = self.locale_translation
        if translation and translation.seedfinder:
            return translation.seedfinder
        return self.seedfinder
    # Strain.locale_seedfinder
    
    @property
    def locale_homepage(self):
        translation = self.locale_translation
        if translation and translation.homepage:
            return translation.homepage
        return self.homepage
        
    @property
    def locale_added_by(self):
        translation = self.locale_translation
        if translation:
            return translation.added_by
        return None
    
# Strain class

class StrainTranslation(models.Model):
    strain = models.ForeignKey(Strain,on_delete=models.CASCADE)
    language = models.ForeignKey(Language,on_delete=models.RESTRICT)
    homepage = models.CharField(max_length=512,
                                blank=True,
                                null=True,
                                default="",
                                validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    seedfinder = models.CharField(max_length=512,
                                  default="",
                                  blank=True,
                                  null=True,
                                  validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    info = models.TextField(default="")
    description = models.TextField(default="")
    added_by = models.ForeignKey(User,
                                 related_name='strain_translation',
                                 editable=False,
                                 null=True,
                                 on_delete=models.RESTRICT)
    added_on = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User,
                                  related_name='strain_translation_edited',
                                  editable=False,
                                  null=True,
                                  on_delete=models.RESTRICT)
    edited_on = models.DateTimeField(auto_now=True)
    
    def validate(self):
        try:
            s = StrainTranslation.objects.get(strain=self.strain.id,
                                              language=self.language.id)
            if self.id != s.id:
                raise ValidationError(_('Strain has already a translation in sepcified language!'))
        except StrainTranslation.DoesNotExist:
            pass
# StrainTranslation class
            
class StrainBackup(models.Model):
    breeder = models.ForeignKey(Breeder,
                                null=True,
                                on_delete=models.SET_NULL)
    strain = models.ForeignKey(Strain,  
                               null=True,
                               on_delete=models.SET_NULL)
    strain_translation = models.ForeignKey(StrainTranslation,
                                           null=True,
                                           on_delete=models.SET_NULL)
    language = models.ForeignKey(Language,
                                 related_name='language',
                                 on_delete=models.RESTRICT)
    breeder_name = models.CharField(max_length=128)
    breeder_key = models.CharField(max_length=64)
    key = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    homepage = models.CharField(max_length=512,
                                null=True,
                                blank=True,
                                validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    seedfinder = models.CharField(max_length=512,
                                  null=True,
                                  blank=True,
                                  validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    info = models.TextField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    edited_by = models.ForeignKey(User,
                                  editable=False,
                                  related_name='strain_backup_edited',
                                  on_delete=models.RESTRICT)
    edited_on = models.DateTimeField(editable=False)
    
    backup_by = models.ForeignKey(User,
                                  editable=False,
                                  related_name='strain_backup',
                                  on_delete=models.RESTRICT)
    backup_on = models.DateTimeField(auto_now_add=True,
                                     editable=False)
# StrainBackup class

