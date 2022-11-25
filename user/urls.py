from django.urls import path

from . import views

app_name = "user"

urlpatterns = [
    path('profile/<int:user_id>/',views.profile,name='profile')
]

