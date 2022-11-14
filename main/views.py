from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import auth
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import get_password_validators,password_validators_help_texts,validate_password
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.core.mail import BadHeaderError,send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.contrib.auth.decorators import permission_required
from django.urls import reverse

from .models import User
from . import config,functions

def index(request):
    language_code = config.get_locale()
    try:
        index_template = config.INDEX_TEMPLATE[language_code]
    except KeyError:
        index_template = 'main/index/index.html'
        
    context = {
        'user':request.user,
        'language_code':language_code,
    }
    
    context.update(functions.get_sidebar_context(request.user))
    
    if request.user.is_authenticated:
        context['title'] = _("Welcome {username} to MyGrowBook".format(username=request.user.get_full_name()))
    else:
        context['title'] = _("Welcome to MyGrowBook")
    
    return render(request,index_template,context)

def login(request):
    context={
        'language_code':config.get_locale(),
        'topic': _('Log in'),
        'next':reverse('index'),
    }
    
    if request.method == "POST":
        try:
            email = request.POST['email'].lower()
            password = request.POST['password']
            if request.POST['next'] and url_has_allowed_host_and_scheme(request.POST['next'],allowed_hosts=[request.get_host()]):
                context['next'] = request.POST['next']
        except KeyError:
            context['error'] = _("Illegal form used!")
            return render(request,'main/login.html',context)
            
        if not email:
            context['error'] = _("No email-address given!")
            return render(request,'main/login.html',context)
        if not password:
            context['error'] = _("No password given!")
            return render(request,'main/login.html',context)
            
        user = auth.authenticate(request,username=email,password=password)
        if not user:
            context['error'] = _("Email address or password don't match!")
            return render(request,'main/login.html',context)
            
        auth.login(request,user)
        
        return redirect(context['next'])
    # Login form callback
        
    if 'next' in request.GET and url_has_allowed_host_and_scheme(request.GET['next'],allowed_hosts=[request.get_host()]):
        context['next'] = request.GET['next']
    
    return render(request,'main/login.html',context)
# login()

def logout(request):
    auth.logout(request)
    return redirect(reverse('index'))
# logout()

def signup(request):
    password_validators = get_password_validators(settings.AUTH_PASSWORD_VALIDATORS)
    context = {
        'language_code':config.get_locale(),
        'topic': _("Sign Up"),
        'email':'',
        'username':'',
        'next':reverse('index'),
        'password_validators_help': password_validators_help_texts(password_validators)
    }
    if request.method == 'POST':
        email_in_use = False
        email = request.POST['email'].lower()
        try:
            User.objects.get(email=email)
            email_in_use = True
        except User.DoesNotExist:
            context['email'] = email
            
        name_in_use = False
        try:
            User.objects.get(name=request.POST['username'])
            name_in_use = True
        except User.DoesNotExist:
            context['username'] = request.POST['username']
            
        if url_has_allowed_host_and_scheme(request.POST['next'],allowed_hosts=[request.get_host()]):
            context['next'] = request.POST['next']
        
        if email_in_use:
            context['error'] = _("Email address is already in use!")
            return render(request,'main/signup.html',context)
        if name_in_use:
            context['error'] = _("Username is already in use!")
            return render(request,'main/sginup.html',context)
        
        password0 = request.POST['password0']
        password1 = request.POST['password1']
        if password0 != password1:
            context['error'] = _("Passwords don't match!")
            return render(request,'main/signup.html',context)
        try: 
            validate_password(password0,
                              user=None,
                              password_validators=password_validators)
        except ValidationError as error:
            context['error'] = str(error)
            return render(request,'main/signup.html',context)
            
        user = User.objects.create(email=context['email'],name=context['username'])
        if user:
            user.set_password(password0)
            user.save()
            user.make_member()
        return redirect(context['next'])                
    else:
        if 'next' in request.GET and is_safe_url(request.GET['next'],allowed_hosts=[request.get_host()]):
            context['next'] = request.GET('next')
        return render(request,'main/signup.html',context)
# signup()

def password_reset_request(request):
    context = {
        'language_code': config.get_locale()
    }
    if request.method == 'POST':
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            try:
                user = User.objects.get(email=data)
                subject = "Password Reset Requested"
                try:
                    email_template = config.RESET_PASSWORD_MAIL_TEMPLATE[config.get_locale()]
                except KeyError:
                    email_template = 'main/password/password_reset_mail.txt'
                context.update({
                    'email': user.email,
                    'username': user.get_full_name(),
                    'domain': request.get_host(),
                    'site_name': 'MyGrowBook.org',
                    'user': user,
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                    'token': default_token_generator.make_token(user),
                    'protocol': settings.SITE_SECURE_PROTOCOL,                    
                })
                email = render_to_string(email_template,context)
                try:
                    send_mail(subject,email,settings.EMAIL_ADDRESS_NOREPLY,[user.email])
                except BadHeaderError:
                    return HttpResponse(request,_('Invalid header found!'))
            except User.DoesNotExist:
                pass
            return redirect(reverse('password_reset_done'))
    # request.method == 'POST'
    context.update({
        'topic': _("Reset Password"),
        'password_reset_form': PasswordResetForm()
    })
    return render(request,'main/password/password_reset_request.html',context)
# password_reset_request()

@permission_required('group.manage',login_url='/login/')
def group(request):
    return HttpResponse('/group/')
# group()
    
@permission_required('group.manage',login_url='/login/')
def group_manage(request,group_id):
    return HttpResponse('/group/{}/'.format(group_id))
# group_manage()
    
@permission_required('user.manage',login_url='/login/')
def user(request):
    return HttpResponse('/user/')
# user()
    
@permission_required('user.manage',login_url='/login/')
def user_manage(request,user_id):
    return HttpResponse('/user/{}/'.format(user_id))
# user_manage()

