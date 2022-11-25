from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.utils.translation import gettext as _
from django.contrib.auth.decorators import permission_required,login_required

# Create your views here.

def index(request):
    return HttpResponse('/user/index')

@login_required(login_url='/login/')
def profile(request,user_id):
    return HttpResponse("/user/profile/{}/".format(user_id))
