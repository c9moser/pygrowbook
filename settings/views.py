from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def index(request):
    return HttpResponse('MyGrowBook/settings/index')
    
def user(request,user_id):
    return HttpResponse('MyGrowBook/settings/user/{}'.format(user_id))
    
