from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path('',views.index,name='index'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('register/',views.register,name='register'),
    path('settings/',views.settings,name='settings'),
    path('manage/',views.manage,name='manage'),
    path('manage/<int:user_id>/',views.manage_user,name='manageuser'),
]

