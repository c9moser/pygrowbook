#-*- coding:utf-8 -*-
from django.contrib.auth.models import Group,Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from .models import Language

from . import config
from growlog.config import init_app as init_growlog_app

def get_group(group):
    if isinstance(group,Group):
        return group
    elif isinstance(group,int):
        try:
            return Group.objects.get(pk=group)
        except Group.DoesNotExist:
            pass
    elif isinstance(group,str):
        try:
            return Group.objects.get(name=group)
        except Group.DoesNotExist:
            pass
    else:
        raise ValueError('group is not a int, str or django.contrib.auth.models.Group instance!')
    return None
# get_group()

def get_permission(permission):
    if isinstance(permission,Permission):
        return permission
    elif isinstance(permission,int):
        try:
            return Permission.objects.get(pk=permission)
        except Permission.DoesNotExist:
            pass
    elif isinstance(permission,str):
        try:
            return Permission.objects.get(codename=permission)
        except Permission.DoesNotExist:
            pass
    else:
        raise ValueError('permission is not a int, str or django.contrib.auth.models.Permission instance!')
    return None
# get_permission()

def add_group_permission(group,permission):
    g = get_group(group)
    if not g:
        return False
        
    perm = get_permission(permission)
    if not perm:
        return False
        
    try:
        perm.group_set.get(id=g.id)
        return False
    except Group.DoesNotExist():
        perm.group_set.add(g.id)
        return True
# add_group_permission

def group_has_permission(group,permission):
    g = get_group(group)
    if not g:
        return False
        
    perm = get_permission(permission)
    if not perm:
        return False
        
    try:
        permission.group_set.get(id=group.id)
        return True
    except Group.DoesNotExist:
        pass
    return False
# group_has_permission()

def create_project_groups():
    for group_name,permissions in config.PROJECT_GROUPS:
        group = get_group(group_name)
        if not group:
            group = Group.objects.create(name=group_name)
        for perm_str in permissions:
            try:
                perm = Permission.objects.get(codename=perm_str)
                if not group_has_permission(group,perm):
                    group.permissions.add(perm)
            except Permission.DoesNotExist:
                pass
# def create_project_groups()

def create_extra_permissions():
    for perm_str,description,model in config.EXTRA_PERMISSIONS:
        try:
            perm = Permission.objects.get(codename=perm_str)
            perm.name = description
            perm.save()
        except Permission.DoesNotExist:
            content_type = ContentType.objects.get_by_model(model)
            perm = Permission.objects.create(codename=perm_str,
                                             name=description,
                                             content_type=content_type)
    
def init_project():
    Language.update()
    create_extra_permissions()
    create_project_groups()
    init_growlog_app()
# init_project()

def get_sidebar_context(user):
    context = {
        'user_is_group_manager': False,
        'user_can_manage_users': False,
        'user_is_user_manager': False,
        'user_is_forum_operator':False,
        'user_is_strainbrowser_operator':False,
        'user_is_wiki_operator':False,
    }  
    if user and user.is_authenticated:
        if user.has_perm('group.manage'):
            context['user_is_group_manager'] = True
        if user.has_perm('user.manage'):
            context['user_can_manage_users'] = True
            context['user_is_user_manager'] = True
        if user.has_perm('strainbrowser.operator'):
            context['user_can_manage_users'] = True
            context['user_is_strainbrowser_operator'] = True
        #TODO
        
    return context
# get_sidebar_context()

def get_supported_languages():
    """
        @return a 2-tuple (language_code,language_name)
    """
    languages = []
    for lang in Language.objects.all():
        inserted = False
        name = _(lang.name)
        for j in range(len(languages)):
            if name < languages[j][1]:
                inserted = True
                languages.insert(j,(lang.locale,name))
        if not inserted:
            languages.append((lang.locale,name))
    return languages
# get_supported_languages()
