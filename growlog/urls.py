#-*- coding:utf-8 -*-

from django.urls import path

from . import views

app_name='growlog'
urlpatterns= [
    path('',views.index,name='index'),
    path('growlog/<int:growlog_id>/',views.growlog,name='growlog'),
]
