#-*- coding:utf-8 -*-

from django.urls import path
from . import views

app_name="forum"
urlpatterns = [
    path('',views.index,name='index'),
]