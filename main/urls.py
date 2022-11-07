#-*- coding:utf-8 -*-
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name="main"

urlpatterns = [
    path('',views.index, name='index'),
    path('login/',views.login, name='login'),
    path('logout/',views.logout,name='logout'),
    path('signup/',views.signup,name='signup'),
    path('password_reset/',views.password_reset_request,name='password_reset_request'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='user/password/password_reset_done.html'), 
         name='password_reset_done'),
    path('password_reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name="user/password/password_reset_confirm.html"), 
         name='password_reset_confirm'),
    path('password_reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='main/password/password_reset_complete.html'), 
         name='password_reset_complete'),
]

