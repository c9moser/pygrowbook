from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import URLValidator,validate_slug
from django.conf import settings
from main.models import User
from main.models import Language

# Create your models here.

class Breeder(models.Model):
    key = models.CharField(max_length=64,
                           unique=True,
                           validators=[validate_slug])
    name = models.CharField(max_length=128)
    seedfinder = models.CharField(max_length=512,
                                  blank=True,
                                  default="",
                                  validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    homepage = models.CharField(max_length=512,
                                blank=True,
                                default="",
                                validators=[URLValidator(schemes=settings.URL_WEBSITE_SCHEMES)])
    added_by = models.ForeignKey(User,related_name='added_by',null=True,on_delete=models.SET_NULL)
    added_on = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(User,
                                 null=True,
                                 on_delete=models.SET_NULL)
    edited_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        permissions=[
            ('strains.breeder.add',_("Allowed to add breeders")),
            ('strains.breeder.edit',_("Allowed to edit all breeders")),
            ('strains.breeder.delete',_('Allowed to delete breeders')),
        ]

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
    created_by = models.ForeignKey(User,
                                   editable=False,
                                   related_name='created_by',
                                   null=True,
                                   on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True,
                                      editable=False)
    edited_by = models.ForeignKey(User,
                                  editable=False,
                                  related_name='edited_by',
                                  null=True,
                                  on_delete=models.SET_NULL)
    edited_on = models.DateTimeField(auto_now=True,
                                     editable=False)
    
    class Meta:
        permissions=[
            ('strains.strain.translate',_('Allowed to translate strains')),
            ('strains.strain.add',_("Allowed to add strains")),
            ('strains.strain.edit',_("Allowed to edit strains")),
            ('strains.strain.delete',_("Allowed to delete strains")),
        ]

    def validate(self):
        try:
            breeder = Breeder.objects.get(pk=self.breeder.id)
        except Breeder.DoesNotExist:
            raise ValidationError('Breeder does not exist!')
            
        try:
            s = breeder.strain_set.get(key=self.key)
            if s.id != self.id:
                raise ValidationError(_('Breeder-key is already in use!'))
        except Strain.DoesNotExist:
            pass
            
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
    
    def validate(self):
        try:
            s = StrainTranslation.objects.get(strain=self.strain.id,
                                              language=self.language.id)
            if self.id != s.id:
                raise ValidationError(_('Strain has already a translation in sepcified language!'))
        except StrainTranslation.DoesNotExist:
            pass
            
            
class StrainBackup(models.Model):
    strain = models.ForeignKey(Strain,on_delete=models.RESTRICT)
    language = models.ForeignKey(Language,
                                 related_name='language',
                                 on_delete=models.RESTRICT)
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
    backup_by = models.ForeignKey(User,
                                  editable=False,
                                  related_name='backup_by',
                                  on_delete=models.SET_NULL,
                                  null=True)
    backup_on = models.DateTimeField(auto_now_add=True,
                                     editable=False)
                                    
