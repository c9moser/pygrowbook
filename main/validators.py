#-*- coding:utf-8 -*-

from django.core.exceptions import ValidationError
from django.config import settings

def validate_password_strength(value):
    if not any(char.isdigit() in char for char in value):
        raise ValidationError(_('Password needs to contain atleast 1 digit!'))
    if not any(char.isalpha() in char for char in value):
        raise ValidationError(_('Password needs to contain atleast 1 character!'))

class PasswordStrengthValidator:
    def validate(password,user=None):
        if not any(char.isdigit() in char for char in password):
            raise ValidationError(_('Password needs to contain atleast 1 digit!'))
        if not any(char.isalpha() in char for char in password):
            raise ValidationError(_('Password needs to contain atleast 1 character!'))
            
    def get_help_text(self):
        return _('Password needs to contain atleast 1 character and one digit.')
    
