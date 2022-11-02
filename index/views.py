from django.shortcuts import render
from django.http import HttpResponse

from django.utils.translation import gettext as _

from . import data
# Create your views here.


def index(request):
    try:
        index_template=data.INDEX_TEMPLATES[data.get_language_code()]
    except KeyError:
        index_template=data.INDEX_TEMPLATES['en-US']

    context = {
        'language_code': data.get_language_code()
    }
    return render(request,index_template,context)

