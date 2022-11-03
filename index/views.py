from django.shortcuts import render
from django.http import HttpResponse

from django.utils.translation import gettext as _

from . import data
# Create your views here.


def index(request):
    try:
        language_code = data.get_language_code()
        index_template=data.INDEX_TEMPLATES[language_code]        
    except KeyError:
        language_code='en-US'
        index_template=data.INDEX_TEMPLATES['en-US']

    context = {
        'user': request.user,
        'language_code':language_code,
    }
    
    if request.user.is_authenticated:
        context['title'] = _("Welcome {user} to MyGrowBook".format(user=request.user.get_short_name()))
    else:
        context['title'] = _("Welcome to MyGrowBook")
        
    return render(request,index_template,context)

