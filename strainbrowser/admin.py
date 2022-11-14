from django.contrib import admin
from .models import Breeder,Strain,StrainBackup,StrainTranslation
# Register your models here.

admin.site.register(Breeder)
admin.site.register(Strain)
admin.site.register(StrainTranslation)
admin.site.register(StrainBackup)
