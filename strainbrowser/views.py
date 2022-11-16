from django.shortcuts import render,redirect,get_object_or_404
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import PermissionDenied
from .models import Breeder,Strain,StrainBackup

from main import config
from .functions import get_context_variables
from .forms import BreederForm,StrainForm,StrainTranslationForm

# Create your views here.

def index(request):
    context = {
        'title': _('MyGrowBook StrainBrowser'),
        'language_code':config.get_locale(),
        'author': 'Christian Moser',
        'head_title': _('MyGrowBook: StrainBrowser'),
        'head_description': _('StrainBrowser Home'),
        'breeder_count': Breeder.objects.all().count(),
        'strain_count': Strain.objects.all().count(),
        'url_breeder_home': reverse('strainbrowser:breeder'),
        'url_breeder_add': reverse('strainbrowser:breeder_add'),
    }
    context.update(get_context_variables(request.user))
    
    return render(request,'strainbrowser/index/index.html',context)
    
def breeder(request):
    context = {
        'title': _("MyGrowBook Breeders"),
        'language_code':config.get_locale(),
        'author': 'Christian Moser',
        'head_title': _('MyGrowBook: Breeders'),
        'head_description': _('Breeder list'),
        'breeder_list': Breeder.objects.filter(pk__gt = 0).order_by('name'),
    }
    context.update(get_context_variables(request.user))
    
    for breeder in context['breeder_list']:
        breeder.strain_count = breeder.strain_set.all().count()
        if context['user_breeder_edit']:
            breeder.user_edit = True
        elif request.user and request.user.is_authenticated():
            breeder.user_edit = (breeder.added_by.id == user.id)
        else:
            breeder.user_edit = False
    
    return render(request,'strainbrowser/breeder/breeder.html',context)
# breeder()
  
def breeder_overview(request,breeder_key):
    breeder = get_object_or_404(Breeder,key=breeder_key)
    context = {
        'language_code': config.get_locale(),
        'author': "Christian Moser",
        'title': breeder.name,
        'head_title':_("MyGrowBook: {breeder}").format(breeder=breeder.name),
        'head_description':_("MyGrowBook - Breeder overview - {breeder}").format(breeder=breeder.name),
        'breeder': breeder,
        'strain_list': breeder.strain_set.all().order_by('name'),
    }
    context.update(get_context_variables(request.user))
    if request.user.is_authenticated():
        if user.has_perm('strainbrowser.breeder.edit') or breeder.added_by.id == request.user.id:
            breeder.user_edit = True
        else:
            breeder.user_edit = False
            
        for strain in context['strain_list']:
            if user.has_perm('strainbrowser.strain.edit') or strain.added_by.id == request.user.id:
                strain.user_edit = True
            else:
                strain.user_edit = False
        
    return render(request,'strainbrowser/breeder/breeder_overview.html',context)
# breeder_overview()


@permission_required('strainbrowser.breeder.add',login_url=reverse('login'))
def breeder_add(request):
    html_template='strainbrowser/breeder/breeder_edit.html'
    context = {
        'language_code': config.get_locale(),
        'author': "Christian Moser",
        'title': _('Add a new Breeder'),
        'head_title': _("MyGrowBook: Breeder Add"),
        'head_description': _('Add a new Breeder'),
        'error_messages' : [],
    }
    context.update(get_context_variables(request.user))
    
    data = {
        'primary_key': 0,        
    }

    if request.method == 'POST':
        form = BreederForm(request.POST,initial=data)
        context['form'] = form
        if not form.validate():
            return form.render(template_name=html_template,context=context)
        
        cdata = form.cleaned_data()
        try:
            Breeder.objects.get(name=cdata['name'])
            context['error_messages'].append(
                _('A Breeder with name "{breeder_name}" already exists!').format(breeder_name=cdata['name'])
        except Breeder.DoesNotExist:
            pass
            
        try:
            Breeder.objects.get(key=cdata['key'])
            context['error_messages'].append(
                _('Breeder key "{breeder_key}" is already in use').format(breeder_key=cdata['key'])
        except Breeder.DoesNotExist:
            pass
            
        if context.error_messages:
            return form.render(template_name=html_template,context=context)
            
        try:
            breeder = Breeder.objects.create(key=context['breeder_key'],
                                             name=context['breeder_name'],
                                             homepage=context['breeder_homepage'],
                                             seedfinder=context['breeder_seedfinder'],
                                             added_by=request.user,
                                             edited_by=request.user)
            return redirect(reverse('strainbrowser:breeder_overview', args=(breeder.key,)))
        except:
            context['error_messages'].append(_("Unable to add breeder to database!"))
        
    return form.render(template_name=html_template,context)
# breeder_add()

@login_required(login_url=reverse('login'))
def breeder_edit(request,breeder_key):
    breeder = get_object_or_404(Breeder,key=breeder_key)
    
    if not user.has_perm('strainbrowser.breeder.edit') and breeder.added_by.id != request.user.id:
        raise PermissionDenied('You are not allowed to edit that breeder!')
    
    html_template = "strainbrowser/breeder/breeder_edit.html"
    
    context = {
        'author': "Christian Moser",
        'title': _("Edit Breeder {breeder}").format(breeder=breeder.name),
        'head_title': _("MyGrowBook: Edit Breeder {breeder}").format(breeder=breeder.name),
        'head_description': _("Edit breeder {breeder}").format(breeder=breeder.name),
        'breeder_name': breeder.name,
        'breeder_key': breeder.key,
        'breeder_homepage': breeder.homepage,
        'breeder_seedfinder': breeder.seedfinder,
        'error_message': None,
    }
    context.update(get_context_variables(request.user))
    
    if request.method == 'POST':
        context['breeder_name'] = request.POST['name']
        context['breeder_key'] = slugify(request.POST['key'])
        context['breeder_homepage'] = request.POST['homepage']
        context['breeder_seedfinder'] = request.POST['seedfinder']
        
        if context['breeder_key'] != request.POST['key']:
            context['error_message'] = _('"{key}" is not a valid key!').format(request.POST['key'])
            return render(request,html_template,context)
            
        try:
            test_breeder = Breeder.objects.get(name=context['breeder_name'])
            if test_breeder.id != breeder.id:
                context['error_message'] = _('Breeder "{breeder}" already exists!').format(breeder=context['breeder_name'])
                return render(request,html_template,context)
        except Breeder.DoesNotExist:
            pass
            
        try:
            test_breeder = Breeder.objects.get(key=context['breeder_key'])
            if test_breeder.id != breeder.id:
                context['error_message'] = _('Breeder with key "{key}" already exists!').format(key=context['breeder_key'])
                return render(request,html_template,context)
        except Breeder.DoesNotExist:
            pass
            
        breeder.name=context['breeder_name']
        breeder.key=context['breeder_key']
        breeder.homepage=context['breeder_homepage']
        breeder.seedfinder=context['breeder_seedfinder']
        breeder.edited_by=request.user
        breeder.save()
        redirect(reverse('strainbrowser:breeder_overview',args=(breeder.key,)))
                
    return render(request,html_template,context)
# breeder_edit

@permission_required('strainbrowser.breeder.delete',login_url=reverse('login'))
def breeder_delete(request,breeder_key):
    #TODO
    return HttpResponse("strainbrowser/breeder_delete/{}/".format(breeder_key))
    
def strain(request,breeder_key,strain_key):
    breeder = get_object_or_404(Breeder,key=breeder_key)
    strain = get_object_or_404(Strain,breeder=breeder.id,key=strain_key)
    
    context = {
        'language_code': config.get_locale(),
        'author': "Christian Moser",
        'title': "<a href=\"{breeder_url}\">{breeder}</a> - {strain}".format(
            breeder_url=reverse('strainbrowser:breeder_overview',args(breeder.key,)),
            breeder=breeder.name,
            strain = strain.name),
        'head_title': _('MyGrowBook: {breeder} - {strain}').format(
            breeder=breeder.name,
            strain=strain.name),
        'head_description': _('MyGrowBook - Strain - {breeder}|{strain}').format(
            breeder=breeder.name,
            strain=strain.name),
        'breeder': breeder,
        'strain': strain,
        'growlog_list': [],
    }
    context.update(get_context_variables(request.user))
    
    if user.has_perm('strainbrowser.strain.edit') or strain.added_by.id == user.id:
        strain.user_edit = True
    else:
        strain.user_edit = False
        
    #TODO:
    #for growlog in strain.growlog_set.all().order_by('title')
        #if growlog.is_visible(request.user):
            #context['growlog_list'].append(growlog)

    return render(request,'strainbrowser/strain/strain.html',context)
# strain()
    
def strain_search(request):
    if not 'search' in request.GET:
        return redirect('/strainbrowser/index')
        
    search = request.GET['search']
    return HttpResponse('/strainbrowser/strain_search<br><b>search:</b> {}'.format(search))


@permission_required('strainbrowser.strain.add')
def strain_add(request,breeder_key):
    return HttpResponse("/strainbrowser/strain_add/{}/".format(breeder.key))
    
@login_required(login_url='/login')
def strain_edit(request,breeder_key,strain_key):
    response = "MyGrowBook/strainbrowser/strain_edit/{}/{}/".format(breeder_key,strain_key)
    return HttpResponse(response)

@permission_required('strainbrowser.strain.delete')
def strain_delete(request,breeder_key,strain_key):
    return HttpResponse("/strainbrowser/strain_delete/{}/{}/".format(breeder_key,strain_key))

def strain_translate(request,breeder_key,strain_key):
    return HttpResponse('MyGrowBook/strainbrowser/strain_translate/{}/{}/'.format(breeder_key,strain_key))
    
def user(request,user_id):
    return HttpResponse('/strainbrowser/user/')

@permission_required('strainbrowser.operator')
def manage_user(request,user_id):
    return HttpResponse("MyGrowBook/strainbrowser/user/{}/".format(user_id))

