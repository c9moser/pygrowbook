#-*- coding:utf-8 -*-

from django.urls import path
from . import views
app_name = "settings"
urlpatterns = [
    path('',views.index,name='index'),
    path('user/',views.user,name='user_settings'),
]

