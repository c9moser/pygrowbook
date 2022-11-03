from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib import auth
from django.utils.translation import gettext as _
from django.utils.http import is_safe_url
from django.contrib.auth.decorators import permission_required

from .models import User
from .functions import create_user_groups


from index import data
# Create your views here.

def index(request):
    return HttpResponse('MyGrowBook/user/index')
    
def login(request):
    context={
        'language_code':data.get_language_code(),
        'next':'/',
    }
    
    if request.method == "POST":
        try:
            email = request.POST['email']
            password = request.POST['password']
            if request.POST['next'] and is_safe_url(request.POST['next'],
                                                    allowed_hosts=[request.get_host()]):
                context['next'] = request.POST['next']
        except KeyError:
            context['error'] = _("Illegal form used!")
            return render(request,'login.html',context)
            
        if not email:
            context['error'] = _("No email-address given!")
            return render(request,'login.html',context)
        if not password:
            context['error'] = _("No password given!")
            return render(request,'login.html',context)
            
        user = auth.authenticate(request,username=email,password=password)
        if not user:
            context['error'] = _("Email-address or password does not match!")
            return render(request,'login.html',context)
            
        auth.login(request,user)
        
        return redirect(context['next'])
        
    else:
        if 'next' in request.GET and is_safe_url(request.GET['next'],
                                                 allowed_hosts=[request.get_host()]):
            context['next'] = request.GET['next']
    
        return render(request,'login.html',context)
# login()
    
def logout(request):
    auth.logout(request)
    return redirect('/')
# logout()
def register(request):
    return HttpResponse('MyGrowBook/user/register/')
# register()
  
def reset_password(request):
    return HttpResponse('MyGrowBook/user/reset_password/')
# reset_password()
    
def settings(request):
    return HttpResponse('MyGrowBook/user/settings/')
# settings()
    
@permission_required('user|manage',login_url='/user/login/')
def manage(request):
    return HttpResponse('MyGrowBook/user/manager/')

@permission_required('user|manage',login_url='/user/login/')
def manage_user(request,user_id):
    return HttpResponse('MyGrowBook/user/manage_user/')
    
