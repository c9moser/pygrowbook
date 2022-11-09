#-*- coding:utf-8 -*-

from django.contrib.auth.base_user import BaseUserManager

class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self,email,password,**extra_fields):
        """ 
        Creates and saves a given user with email and password 
        """
        
        if not email:
            raise ValueError('email must be set!')
            
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    # UserManager._create_user()
    
    def create_user(self,email,password=None,**extra_fields):
        extra_fields.setdefault('is_superuser',False)
        extra_fields.setdefault('is_staff',False)
        
        user = self._create_user(email,password,**extra_fields)
        if user:
            user.make_member()
            
        return user
    # UserManager.create_user()
        
    def create_superuser(self,email,password,**extra_fields):
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_staff',True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True!')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True!')
            
        user = self._create_user(email,password,**extra_fields)
        if user:
            user.make_member()
            user.make_superuser()
            
        return user
    # UserManager.create_superuser()
    