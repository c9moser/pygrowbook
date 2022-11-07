#-*- coding:utf-8 -*-
from django.contrib.auth.models import Group,Permission
from . import config

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


