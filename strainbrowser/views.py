#-*- coding:utf-8 -*-
import os
from django.shortcuts import render,redirect,get_object_or_404
from django.utils.translation import gettext as _
from django.utils.text import slugify
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import permission_required,login_required
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from .models import Breeder,Strain,StrainTranslation,StrainBackup
from main.models import Language
from main import config as main_config
from .config import COMPRESSION


from .functions import get_context_variables
from .forms import BreederForm,StrainForm,StrainTranslationForm

from django.conf import settings

# Create your views here.

def index(request):
    context = {
        'title': _('GrowBook StrainBrowser'),
        'language_code':main_config.get_locale(),
        'author': 'Christian Moser',
        'head_title': _('GrowBook: StrainBrowser'),
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
        'title': _("GrowBook Breeders"),
        'language_code':main_config.get_locale(),
        'author': 'Christian Moser',
        'head_title': _('GrowBook: Breeders'),
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
    locale = main_config.get_locale()
    context = {
        'language_code': locale,
        'author': "Christian Moser",
        'title': breeder.name,
        'head_title':_("GrowBook: {breeder}").format(breeder=breeder.name),
        'head_description':_("GrowBook - Breeder overview - {breeder}").format(breeder=breeder.name),
        'breeder': breeder,
        'strain_list': breeder.strain_set.all().order_by('name'),
    }
    context.update(get_context_variables(request.user))
    if request.user.is_authenticated:
        if (request.user.has_perm('strainbrowser.breeder.edit') 
                or breeder.added_by.id == request.user.id):
            breeder.user_edit = True
        else:
            breeder.user_edit = False
            
        for strain in context['strain_list']:
            if (request.user.has_perm('strainbrowser.strain.edit') 
                    or strain.added_by.id == request.user.id):
                strain.user_edit = True
            else:
                strain.user_edit = False
                
            strain.user_translate = False
            
            if locale != 'en-US':
                try:
                    translation = strain.straintranslation_set.get(language__locale=locale)
                except StrainTranslation.DoesNotExist:
                    translation = None
                    
                if request.user.has_perm('strainbrowser.strain.translate') or not translation:
                    strain.user_translate = True
        # endfor strain
        
    return render(request,'strainbrowser/breeder/breeder_overview.html',context)
# breeder_overview()


@permission_required('strainbrowser.breeder.add',login_url='/login/')
def breeder_add(request):
    html_template='strainbrowser/breeder/breeder_edit.html'
    context = {
        'language_code': main_config.get_locale(),
        'author': "Christian Moser",
        'title': _('Add a new Breeder'),
        'head_title': _("GrowBook: Breeder Add"),
        'head_description': _('Add a new Breeder'),
        'error_messages' : [],
        'submit_button': _('Add Breeder')
    }
    context.update(get_context_variables(request.user))
    
    data = {
        'primary_key': 0,        
    }

    form = None
    if request.method == 'POST':
        form = BreederForm(request.POST,data)
        context['form'] = form
        if not form.is_valid():
            return form.render(template_name=html_template,context=context)
        
        cdata = form.cleaned_data
        try:
            Breeder.objects.get(name=cdata['name'])
            context['error_messages'].append(
                _('A Breeder with name "{breeder_name}" already exists!').format(breeder_name=cdata['name']))
        except Breeder.DoesNotExist:
            pass
            
        try:
            Breeder.objects.get(key=cdata['key'])
            context['error_messages'].append(
                _('Breeder key "{breeder_key}" is already in use').format(breeder_key=cdata['key']))
        except Breeder.DoesNotExist:
            pass
            
        if context['error_messages']:
            return render(request,html_template,context)
            
        try:
            breeder = Breeder.objects.create(key=cdata['key'],
                                             name=cdata['name'],
                                             homepage=cdata['homepage'],
                                             seedfinder=cdata['seedfinder'],
                                             added_by=request.user,
                                             edited_by=request.user)
            return redirect(reverse('strainbrowser:breeder_overview', args=(breeder.key,)))
        except Exception as error:
            context['error_messages'].append(_("Unable to add breeder to database! ({})".format(error)))
        
    if not form:
        form = BreederForm(data)
        context['form'] = form
        print(context['form'])
    return render(request,html_template,context)
# breeder_add()

@login_required(login_url='/login/')
def breeder_edit(request,breeder_key):
    breeder = get_object_or_404(Breeder,key=breeder_key)
    
    if not request.user.has_perm('strainbrowser.breeder.edit') and breeder.added_by.id != request.user.id:
        raise PermissionDenied('You are not allowed to edit that breeder!')
    
    html_template = "strainbrowser/breeder/breeder_edit.html"
    
    context = {
        'author': "Christian Moser",
        'title': _("Edit Breeder {breeder}").format(breeder=breeder.name),
        'head_title': _("GrowBook: Edit Breeder {breeder}").format(breeder=breeder.name),
        'head_description': _("Edit breeder {breeder}").format(breeder=breeder.name),
        'error_messages': [],
        'submit_button': _("Save Breeder")
    }
    context.update(get_context_variables(request.user))
    data = {
        'primary_key': breeder.id,
        'key': breeder.key,
        'name': breeder.name,
        'homepage': breeder.homepage,
        'seedfinder': breeder.seedfinder,
    }

    form = None
    if request.method == "POST":
        form = BreederForm(request.POST,data)
        context['form'] = form
        if form.is_valid():
            if form.cleaned_data['primary_key'] != strain.id:
                context['error_messages'] = _('Illegal form! (Primary key mismatch)')
            if 'key' in form.changed_data:
                key_ok = True
                try:
                    test_breeder = Breeder.objects.get(key=form.cleaned_data['key'])
                    if test_breeder.id != breeder.id:
                        key_ok = False
                        context['error_messages'].append(
                            _("Breeder key \"{key}\" is already in use!").format(key=form.cleaned_data['key']))
                except Breeder.DoesNotExist:
                    pass
                if key_ok:
                    breeder.key = form.cleaned_data['key']
            
            if 'name' in form.changed_data:
                name_ok = True
                try:
                    test_breeder = Breeder.objects.get(name=form.cleaned_data['name'])
                    if test_breeder.id != breeder.id:
                        name_ok = False
                        context['error_messages'].append(
                            _('Breeder name \"{name}\" is already in use!').format(name=form.cleaned_data['name']))
                except Breeder.DoesNotExist:
                    pass
                if name_ok:
                    breeder.name = form.cleaned_data['name']
                        
            if 'homepage' in form.changed_data:
                breeder.homepage = form.cleaned_data['homepage']
            if 'seedfinder' in form.changed_data:
                breeder.seedfinder = form.cleaned_data['seedfinder']
                
            if context['error_messages']:
                return render(request,html_template,context)
                
            breeder.save()
            return redirect(reverse('strainbrowser:breeder_overview',args=(breeder.key,)))
    if not form:
        form = BreederForm(data)
        context['form'] = form
        
    return render(request,html_template,context)
# breeder_edit

def breeder_export(request,breeder_id):
    breeder = get_object_or_404(Breeder,key=breeder_id)
    return HttpResponse('/strainbrowser/breeder_export/')

def real_breeder_export(request,breeder_id):
    breeder = get_object_or_404(Breeder,key=breeder_id)
    if 'compress' in request.GET:
        compression = request.GET['compress']
    return HttpResponse('/strainbrowser/real_breeder_export/')
            
def breeder_export_done(request):
    context = {
        'breeder': None,
    }
    if 'breeder' in request.GET:
        breeder = get_object_or_404(request.GET['breeder'])
        context['breeder'] = breeder
    if 'export' not in request.GET:
        pass
        
@permission_required('strainbrowser.breeder.delete',login_url='/login/')
def breeder_delete(request,breeder_key):
    #TODO
    return HttpResponse("strainbrowser/breeder_delete/{}/".format(breeder_key))
    
def strain(request,breeder_key,strain_key):
    breeder = get_object_or_404(Breeder,key=breeder_key)
    strain = get_object_or_404(Strain,breeder=breeder.id,key=strain_key)
    locale = main_config.get_locale()
    try:
        language = Language.objects.get(locale=locale)
    except Language.DoesNotExist:
        language = None
        
    context = {
        'language_code': locale,
        'author': "Christian Moser",
        'title': "<a href=\"{breeder_url}\">{breeder}</a> - {strain}".format(
            breeder_url=reverse('strainbrowser:breeder_overview',args=(breeder.key,)),
            breeder=breeder.name,
            strain = strain.name),
        'head_title': _('GrowBook: {breeder} - {strain}').format(
            breeder=breeder.name,
            strain=strain.name),
        'head_description': _('GrowBook - Strain - {breeder}|{strain}').format(
            breeder=breeder.name,
            strain=strain.name),
        'breeder': breeder,
        'strain': strain,
        'growlog_list': strain.get_growlogs(request.user),
    }
    context.update(get_context_variables(request.user))
    
    strain.user_can_edit = False
    strain.user_can_translate = False
    if request.user:
        if (request.user.has_perm('strainbrowser.strain.edit') 
                or strain.added_by.id == request.user.id):
            strain.user_can_edit = True
        if language and language.locale != 'en-US':
            try:
                translation = strain.straintranslation_set.get(language__locale=language.locale)
                if (request.user.has_perm('strainbrowser.strain.translate')
                        or translation.added_by.id == request.user.id):
                    strain.user_can_translate = True
            except StrainTranslation.DoesNotExist:
                strain.user_can_translate = True
    # END strain permissions
            
    strain_translation = None
            
    if (request.user.has_perm('strainbrowser.strain.edit') 
            or strain.added_by.id == request.user.id):
        strain.user_edit = True
    else:
        strain.user_edit = False
        
    strain.user_translate = False
    if main_config.get_locale() != 'en-US' and request.user and request.user.is_authenticated:
        if (not strain_translation
                or user.has_perm('strainbrowser.strain.translate')
                or strain_translation.added_by.id == request.user.id):
            strain.user_translate = True
    
    return render(request,'strainbrowser/strain/strain.html',context)
# strain()
    
def strain_search(request):
    if not 'search' in request.GET:
        return redirect('/strainbrowser/index')
        
    search = request.GET['search']
    return HttpResponse('/strainbrowser/strain_search<br><b>search:</b> {}'.format(search))


@permission_required('strainbrowser.strain.add',login_url='/login/')
def strain_add(request,breeder_key):
    html_template = 'strainbrowser/strain/strain_edit.html'
    breeder = get_object_or_404(Breeder,key=breeder_key)
    
    context = {
        'language_code': main_config.get_locale(),
        'title': _("Add a strain to {breeder}").format(
            breeder='<a href="{}">{}</a>'.format(
                reverse('strainbrowser:breeder_overview',args=(breeder.key,)),
                breeder.name)),
        'author': "Christian Moser",
        'head_title': _("GrowBook: Add a strain").format(breeder=breeder.name),
        'head_description': 
            _("GrowBook - Add a strain to breeder {breeder}").format(breeder=breeder.name),
        'breeder': breeder,
        'error_messages': [],
        'submit_button': _("Add Strain"),
    }
    context.update(get_context_variables(request.user))
    data = {
        'primary_key': 0,
        'breeder_key': breeder.key,
    }
    form = None
    if request.method == 'POST':
        form = StrainForm(request.POST,data)
        context['form'] = form
        
        if form.is_valid():
            if form.cleaned_data['breeder_key'] != breeder.key:
                context['error_messages'].append(
                    _('Illegal form! (Breeder key mismatch)!'))
            try: 
                breeder.strain_set.get(key=form.cleaned_data['key'])
                context['error_messages'].append(
                    _('Breeder {breeder} has already a strain-key {key}!').format(
                        breeder=breeder.name,
                        key=form.cleaned_data['key']))
            except Strain.DoesNotExist:
                pass
                
            try:
                breeder.strain_set.get(key=form.cleaned_data['key'])
                context['error_messages'].append(
                    _('Breeder {breeder} has already a strain named {name}!').format(
                        breeder=breeder.name,
                        name=form.cleaned_data['name']))
            except Strain.DoesNotExist:
                pass
                
            if not context['error_messages']:
                kwargs = {
                    'breeder': breeder,
                    'name': form.cleaned_data['name'],
                    'key': form.cleaned_data['key'],
                    'added_by': request.user,
                    'edited_by': request.user,
                }
                if form.cleaned_data['info']:
                     kwargs['info'] = form.cleaned_data['info']
                if form.cleaned_data['description']:
                    kwargs['description'] = form.cleaned_data['description']
                if form.cleaned_data['homepage']:
                    kwargs['homepage'] = form.cleaned_data['homepage']
                if form.cleaned_data['seedfinder']:
                    kwargs['seedfinder'] = form.cleaned_data['seedfinder']
                
                try:    
                    strain = Strain.objects.create(**kwargs)
                    return redirect(reverse('strainbrowser:strain',
                                    args=(breeder.key,strain.key)))
                except Exception as error:
                    context['error_messages'].append(
                        _('Unable to create strain! ({error})').format(error))
    if not form:
        form = StrainForm(data)
        context['form'] = form
    return render(request,html_template,context)
# strain_add()
    
@login_required(login_url='/login')
def strain_edit(request,breeder_key,strain_key):
    strain = get_object_or_404(Strain,breeder__key=breeder_key,key=strain_key)
    html_template = 'strainbrowser/strain/strain_edit.html'
    
    if (not request.user.has_perm('strainbrowser.strain.edit') 
            and strain.added_by.id != request.user.id):
        raise PermissionDenied(_("You are not allowed to edit this strain!"))
        
    context = {
        'language_code': main_config.get_locale(),
        'author': "Christian Moser",
        'title': _("Growbook: Edit Strain {breeder} - {strain}").format(
            breeder='<a href="{}">{}</a>'.format(
                reverse('strainbrowser:breeder_overview',args=(strain.breeder.key,)),
                strain.breeder.name),
            strain=strain.name),
        'head_title': _('GrowBook: Edit Strain'),
        'head_description': _("GrowBook: Edit strain {breeder} - {strain}"),
        'breeder': strain.breeder,
        'error_messages': [],
        'submit_button': _("Save Strain"),
    }
    context.update(get_context_variables(request.user))
    
    data = {
        'breeder_key': strain.breeder.key,
        'primary_key': strain.id,
        'name': strain.name,
        'key': strain.key,
        'homepage': strain.homepage,
        'seedfinder': strain.seedfinder,
        'info': strain.info,
        'description': strain.description,
    }
    
    form=None
    if request.method == "POST":
        form = StrainForm(request.POST,data)
        context['form'] = form
        
        if form.is_valid():
            if form.cleaned_data['breeder_key'] != breeder_key:
                context['error_messages'].append(_("Breeder key mismatch!"))
            
            if 'key' in form.changed_data:
                try:
                    test_strain = strain.breeder.strain_set.get(key=form.cleaned_data['key'])
                    if test_strain.id != strain.id:
                        context['error_messages'].append(
                            _('Breeder {breeder} has already a strain-key {key}!').format(
                                breeder=strain.breeder.name,
                                key=form.cleaned_data['key']))
                except Strain.DoesNotExist:
                    pass
                    
            if 'name' in form.changed_data:
                try:
                    test_strain = strain.breeder.strain_set.get(name=form.cleaned_data['name'])
                    if test_strain.id != strain.id:
                        context['error_messages'].append(
                            _("Breeder {breeder} has already a strain named {name}!").format(
                                breeder=breeder.name,
                                strain=form.cleaned_data['name']))
                except Strain.DoesNotExist:
                    pass
            
            if not context['error_messages']:
                if form.changed_data:
                    StrainBackup.objects.create(
                        strain = strain,
                        language = Language.objects.get(locale='en-US'),
                        name = strain.name,
                        key = strain.key,
                        homepage = strain.homepage,
                        seedfinder = strain.seedfinder,
                        info = strain.info,
                        description = strain.description,
                        edited_by = strain.edited_by,
                        edited_on = strain.edited_on,
                        backup_by = request.user
                    )
                    
                    if 'key' in form.changed_data:
                        strain.key = form.cleaned_data['key']
                    if 'name' in form.changed_data:
                        strain.name = form.cleaned_data['name']
                    if 'homepage' in form.changed_data:
                        strain.homepage = form.cleaned_data['homepage']
                    if 'seedfinder' in form.changed_data:
                        strain.seedfinder = form.cleaned_data['seedfinder']
                    if 'info' in form.changed_data:
                        strain.info = form.cleaned_data['info']
                    if 'description' in form.changed_data:
                        strain.description = form.cleaned_data['description']
                        
                    strain.edited_by = request.user
                    strain.save()
                return redirect(reverse('strainbrowser:strain',args=(strain.breeder.key,strain.key)))
        
    if not form:
        form = StrainForm(data)
        context['form'] = form
    return render(request,html_template,context)
# strain_edit()

@permission_required('strainbrowser.strain.delete',login_url='/login/')
def strain_delete(request,breeder_key,strain_key):
    # TODO
    return HttpResponse("/strainbrowser/strain_delete/{}/{}/".format(breeder_key,strain_key))

@login_required(login_url='/login/')
def strain_translate(request,breeder_key,strain_key,language_code):
    strain = get_object_or_404(Strain,breeder__key=breeder_key,key=strain_key)
    language = get_object_or_404(Language,locale=language_code)
    
    try:
        translation = StrainTranslation.objects.get(strain__id=strain.id,language__id=language.id)
        if (not request.user.has_perm('strainbrowser.strain.translate') 
                and translation.added_by.id != request.user.id):
            raise PermissionDenied(_('You are not allowed to translate this strain!'))
            
    except StrainTranslation.DoesNotExist:
        translation = None
        
    context = {
        'language_code': main_config.get_locale(),
        'author': "Christian Moser",
        'title': _("Growbook: Translate {breeder} - {strain} to {language}").format(
            breeder='<a href="{}">{}</a>'.format(
                reverse('strainbrowser:breeder_overview',args=(strain.breeder.key,)),
                strain.breeder.name),
            strain='<a href="{}">{}</a>'.format(
                reverse('strainbrowser:strain',args=(strain.breeder.key,strain.key)),
                strain.name),
            language=_(language.name)),
        'head_title': _('GrowBook: Translate strain {breeder} - {strain}').format(
            breeder=strain.breeder.name,
            strain=strain.name),
        'head_description': _('GrowBook: Translate strain {breeder} - {strain} to {language}').format(
            breeder=strain.breeder.name,
            strain=strain.name,
            language=language.name),
        'strain': strain,
        'language': language,
        'submit_button': _('Save Tranlation'),
        'error_messages': []
    }
    context.update(get_context_variables(request.user))
    
    data = {
        'breeder_key': strain.breeder.key,
        'strain_key': strain.key,
        'strain_id': strain.id,
        'language': language_code,
    }
    if translation:
        data.update({
            'description': translation.description,
            'info': translation.info,
            'homepage': translation.homepage,
            'seedfinder': translation.seedfinder,
        })
    
    form = None
    if request.method == "POST":
        form = StrainTranslationForm(request.POST,data)
        context['form'] = form
        
        if form.is_valid():
            if not translation:
                kwargs = {
                    'added_by': request.user,
                    'language': language,
                    'strain': strain,
                    'edited_by': request.user,
                }
                if form.cleaned_data['seedfinder']:
                    kwargs['seedfinder'] = form.cleaned_data['seedfinder']
                if form.cleaned_data['homepage']:
                    kwargs['homepage'] = form.cleaned_data['homepage']
                if form.cleaned_data['info']:
                    kwargs['info'] = form.cleaned_data['info']
                if form.cleaned_data['description']:
                    kwargs['description'] = form.cleaned_data['description']
                    
                translation = StrainTranslation.objects.create(**kwargs)
            elif form.changed_data: # have translation
                StrainBackup.objects.create(
                    strain=strain,
                    strain_translation=translation,
                    language=language,
                    key=strain.key,
                    name=strain.name,
                    homepage=translation.homepage,
                    seedfinder=translation.seedfinder,
                    info=translation.info,
                    description=translation.description,
                    edited_by=translation.edited_by,
                    edited_on=translation.edited_on,
                    backup_by=request.user)
                        
                if 'homepage' in form.changed_data:
                    translation.homepage = form.cleaned_data['homepage']
                if 'seedfinder' in form.changed_data:
                    translation.seedfinder = form.cleaned_data['seedfinder']
                if 'info' in form.changed_data:
                    translation.info = form.cleaned_data['info']
                if 'description' in form.changed_data:
                    translation.description = form.cleaned_data['description']
                        
                translation.edited_by = request.user
                translation.save()
            return redirect(reverse('strainbrowser:strain',args=(strain.breeder.key,strain.key)))
        else:
            context['error_messages'].append(_('ILLEGAL FORM'))
            for error in form.errors:
                context['error_messages'].append(error)
    if not form:
        form = StrainTranslationForm(data)
        context['form'] = form
    return render(request,'strainbrowser/strain/strain_translate.html',context)
# strain_translate()
    
   
@permission_required('strainbrowser.operator',login_url='/login/')
def manage_user(request,user_id=None):
    if user_id:
        response="/strainbrowser/manage_user/{}/".format(user_id)
    else:
        response="/strainbrowser/manage_user/"
    return HttpResponse(response)

