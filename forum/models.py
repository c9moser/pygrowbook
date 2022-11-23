from django.db import models
from main.models import User,Language

# Create your models here.
class ForumSections(models.Model):
    name = models.CharField(max_length=64,unique=True)
    title = models.CharField(max_length=256)
    description = models.TextField()
    
class Thread(models.Model):
    section = models.ForeignKey(ForumSections,
                                on_delete=models.RESTRICT)
    language = models.ForeignKey(Language,
                                 on_delete=models.RESTRICT)
    title = models.CharField(max_length=512)
    created_by = models.ForeignKey(User,
                                   related_name='forum_thread',
                                   on_delete=models.RESTRICT)
    created_on = models.DateTimeField(auto_now_add = True)
# Thread()
    
class ThreadPost(models.Model):
    Thread = models.ForeignKey(Thread,
                               on_delete=models.RESTRICT)
    created_by = models.ForeignKey(User,
                                   on_delete=models.RESTRICT,
                                   related_name='forum_post')
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.TextField()
# ThreadPost()

