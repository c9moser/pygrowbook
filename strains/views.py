from django.shortcuts import render

from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse('MyGrowBook/strains/index')
    
def breeder(request,breeder_key):
    response = "MyGrowBook/strains/breeder/{}/".format(breeder_key)
    return HttpResponse(response)

def breeder_edit(request,breeder_key=""):
    if breeder_key:
        response = "MyGrowBook/strains/edit/breeder/{}/".format(breeder_key)
    else:
        response = "MyGrowBook/strains/new/breeder/"
    return HttpResponse(response)
    
def strain(request,breeder_key,strain_key):
    response = "MyGrowBook/strains/strain/{}/{}/".format(breeder_key,strain_key)    

def strain_edit(request,breeder_key,strain_key=""):
    if strain_key:
        response = "MyGrowBook/strains/edit/strain/{}/{}/".format(breeder_key,strain_key)
    else:
        response = "MyGrowBook/strains/new/strain/{}/".format(breeder_id)
