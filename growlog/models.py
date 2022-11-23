from django.db import models
from strainbrowser.models import Breeder,Strain
from main.models import User,Language
from .functions import growlog_image_upload_path

import datetime

# Create your models here.

class GrowlogVisibility(models.Model):
    name = models.CharField(max_length=32)
    description = models.CharField(max_length=256)
# GrowlogVisibility class

class Growlog(models.Model):
    language = models.ForeignKey(Language,
                                 on_delete=models.RESTRICT)
    user = models.ForeignKey(User,
                             editable=False,
                             on_delete=models.RESTRICT)
    visibility = models.ForeignKey(GrowlogVisibility,
                                   on_delete=models.RESTRICT)
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True,
                                   null=True)
    conclusion = models.TextField(blank=True,
                                  null=True)
    strains = models.ManyToManyField(Strain)
    started_on = models.DateTimeField(auto_now_add=True,
                                      editable=False)
    flower_on = models.DateField(null=True,
                                 editable=False)
    finished_on = models.DateTimeField(null=True,
                                       editable=False)
    edited_on = models.DateTimeField(auto_now=True)
    
    class Meta:
        permissions = [
            ('growlog.operator','Growlog Operator'),
        ]
    def __str__(self):
        return self.title
        
    def is_visible(self,user=None):
        if self.visibility.name == 'public':
            return True
        elif user:  
            if self.visibility.name == 'member':
                return user.is_authenticated()
            elif self.visibility.name == 'friend':
                if user.is_in_group('user.{}.friend'.format(self.user.id)):
                    return True
            elif self.visibility.name == 'private':
                return (user.id == self.user.id)
                                
        return False
    # Growlog.is_visible()
    
    @property
    def is_finished(self):
        if self.finished_on:
            return True
        return False
    # Growlog.is_finished
    
    @property
    def is_flowering(self):
        if self.flower_on:
            return True
        return False
    # Growlog.is_flowering
    
    @property
    def age(self):
        """
            Age of the grow in days.
        """
        date_start = datetime.date(self.started_on.year,
                                   self.started_on.month,
                                   self.started_on.day)
        
        if self.is_finished:
            date_end = datetime.date(self.finished_on.year,
                                     self.finished_on.month,
                                     self.finished_on.day)
        else:
            date_end = datetime.date.today()
            
        return (date_end - date_start).days
    # Growlog.age
        
    @property                    
    def flowering_days(self):
        """
           Flowering days of the grow.
        """
        if not self.is_flowering:
            return 0
            
        if self.is_finished:
            self.date_end = datetime.date(self.finished_on.year,
                                          self.finished_on.month,
                                          self.finished_on.day)
        else:
            self.date_end = datetime.date.today()
            
        return (self.date_end - self.flower_on).days
    # Growlog.flowering_days
# Growlog class

class GrowlogEntry(models.Model):
    growlog = models.ForeignKey(Growlog,
                                on_delete=models.CASCADE,
                                editable=False)
    entry = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
    
    @property
    def age(self):
        """
            Age of the entry in days.
        """
        date_start = datetime.date(self.growlog.started_on.year,
                                   self.growlog.started_on.month,
                                   self.growlog.started_on.day)
        date_current = datetime.date(self.created_on.year,
                                     self.created_on.month,
                                     self.created_on.day)
        return (date_current - date_start).days
    # GrowlogEntry.age
    
    @property
    def is_flowering(self):
        if not self.growlog.flower_on:
            return False
            
        date_current = datetime.date(self.created_on.year,
                                     self.created_on.month,
                                     self.created_on.day)
        return (date_current >= self.growlog.flower_on)
    # GrowlogEntry.is_flowering
    
    @property
    def flowering_days(self):
        """
            Flowering time in days.
        """
        if not self.is_flowering:
            return 0
            
        date_current = datetime.date(self.created_on.year,
                                     self.created_on.month,
                                     self.created_on.day)
        return (date_current - self.growlog.flower_on).days
    # GrowlogEntry.flowering_days
# GrowlogEntry class

class GrowlogEntryImage(models.Model):
    entry = models.ForeignKey(GrowlogEntry,
                              on_delete=models.CASCADE)
    strains = models.ManyToManyField(Strain)
    description = models.CharField(max_length=2048,
                                   null=True,
                                   blank=True)
    image = models.ImageField(upload_to=growlog_image_upload_path)
# GrowlogEntryImage class
