from django.db import models
from strainbrowser.models import Breeder,Strain
from main.models import User,Language

# Create your models here.
class Growlog(models.Model):
    language = models.ForeignKey(Language,
                                 required=True,
                                 on_delete=models.RESTRICT)
    user = models.ForeignKey(User,
                             required=True,
                             editable=False,
                             on_delete=models.RESTRICT)
    title = models.CharField(max_length=256,
                             required=True)
    description = models.TextField(required=False,
                                   blank=True,
                                   null=True)
    strains = models.ManyToManyField(Strain)
    started_on = models.DateTimeField(auto_now_add=True,
                                      required=True,
                                      editable=False)
    flower_on = models.DateField(null=True,
                                 required=False,
                                 editable=False)
    finished_on = models.DateTimeField(null=True,
                                       required=False,
                                       editable=False)
    edited_on = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
# Growlog class


class GrowlogEntry(models.Model):
    growlog = models.ForeignKey(Growlog,
                                on_delete=models.CASCADE,
                                required=True,
                                editable=False)
    entry = models.TextField(required=True)
    created_on = models.DateTimeField(auto_now_add=True)
    edited_on = models.DateTimeField(auto_now=True)
# GrowlogEntry class

