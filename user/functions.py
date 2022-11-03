#-*- coding:utf-8 -*-
from django.contrib.auth.models import Group,Permission
from django.utils.translation import gettext_noop as N_

def create_project_groups():
    project_groups = [
        (
            'site-operator',
            (
                'user|manage',
                'forum|operator',
                'wiki|operator',
                'wiki|edit_all',
                'wiki|author',
                'pm|allow_all',
            )
        ),
        (
            'forum-operator', 
            ('forum|operator',)
        ),
        (
            'forum-thread-create',
            ('forum|thread_create',)
        ),
        (
            'forum-thread-post',
            ('forum|thread_post',)
        ),
        (
            'pm-allow-all',
            ('pm|allow_all',)
        ),
        (
            'wiki-operator',
            ('wiki|operator','wiki|edit_all','wiki|author')
        ),
        (
            'wiki-author',
            ('wiki|author',)
        ),
    ]
    for group_name,permissions in project_groups:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            group = Group.objects.create(name=group_name)
            group.save()
            
        permlist = []
        for perm_str in permissions:
            try:
                perm = Permission.objects.get(codename=perm_str)
                permlist.append(perm.id)
            except Permission.DoesNotExist:
                pass
                
        if permlist:
            group.permissions.add(*tuple(permlist))
        group.save()
# def create_project_groups()

def create_default_user_groups(user):
    user_groups = [
        (
            'user{}'.format(user.id), 
            True
        ),
        (
            'user{}-friends'.format(user.id),
            True
        ),
        (
            'user{}-friends-block'.format(user.id),
            False
        ),
        (
            'user{}-pm-block'.format(user.id),
            False
        )
        (
            'user{}-growlog-block'.format(user.id),
            False
        )
    ]
    for group_name,user_add in user_groups:
        group = Group.objects.create(name=group_name)
        permlist = []
        if user_add:
            group.user_set.add(user)
# create_default_user_groups()

def add_user_to_default_groups(user):
    default_groups=[
        'forum-thread-create',
        'forum-thread-post',
        'wiki-author'
    ]    
    for group_name in default_groups:
        group = Group.objects.get(name=group_name)
        if group:
            group.user_set.add(user)
# add_user_to_default_groups()

def add_user_to_superuser_groups(user):
    pass
    
def create_user_groups(user):
    create_default_user_groups(user)
    add_user_to_default_groups(user)
# def create_user_groups()

