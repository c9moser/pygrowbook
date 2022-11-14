#-*- coding:utf-8 -*-

from django.urls import path
from . import views

app_name = "strainbrowser"

urlpatterns = [
    path('',views.index,name='index'),
    path('breeder/',views.breeder,name='breeder'),
    path('breeder/<slug:breeder_key>/',views.breeder_overview,name='breeder_overview'),
    path('breeder_add/',views.breeder_add,name='breeder_add'),
    path('breeder_edit/<slug:breeder_key>',views.breeder_edit,name='breeder_edit'),
    path('breeder_delete/<slug:breeder_key>',views.breeder_delete,name='breeder_delete'),
    path('strain/<slug:breeder_key>/<slug:strain_key>',views.strain,name='strain'),
    path('strain_add/<slug:breeder_key>/',views.strain_add,name='strain_add'),
    path('strain_edit/<slug:breeder_key>/<slug:strain_key>/',views.strain_edit,name='strain_edit'),
    path('strain_delete/<slug:breeder_key>/<slug:strain_key>/',views.strain_delete,name='strain_delete'),
    path('strain_translate/<slug:breeder_key>/<slug:strain_key>/',views.strain_translate,name='strain_translate'),
    path('search/',views.strain_search,name='strain_search'),
    path('user/',views.user,name='user'),
    path('user/<int:user_id>/',views.manage_user,name='manage_user'),
]

