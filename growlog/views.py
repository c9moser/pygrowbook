from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse('MyGrowBook/growlog/index')

def growlog(request,growlog_id):
    return HttpResponse('/growlog/growlog/{}/'.format(growlog_id))
    
def user_growlogs(request,user_id):
    return HttpResponse('/growlog/user_growlogs/{}/'.format(user_id))
