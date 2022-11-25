from django.template.loader import render_to_string
import datetime

from main import functions
from main.models import FileValid

from .config import COMPRESSION

def get_context_variables(user=None,breeder=None,strain=None):
    def _get_breeder_context(user=None,breeder=None):
        context = {
            'user_breeder_add': False,
            'user_breeder_edit': False,
            'user_breeder_delete': False,
        }
        if user and user.is_authenticated:
            if user.has_perm('strainbrowser.breeder.add'):
                context['user_breeder_add'] = True
            
            if user.has_perm('strainbrowser.breeder.edit'):
                context['user_breeder_edit'] = True
            elif breeder:
                context['user_breeder_edit'] = (breeder.added_by.id == user.id)        
        
            if user.has_perm('strainbrowser.breeder.delete'):
                context['user_breeder_delete'] = True
        # user        
        return context
    # _get_breeder_context()
    
    def _get_strain_context(user=None,breeder=None,strain=None):
        context = {
            'user_strain_add': False,
            'user_strain_edit': False,
            'user_strain_delete': False,
        }
        if user and user.is_authenticated:
            if user.has_perm('strainbrowser.strain.add'):
                context['user_strain_add'] = True
            elif breeder:
                context['user_strain_add'] = (breeder.added_by.id == user.id)
                
            if user.has_perm('strainbrowser.strain.edit'):
                context['user_strain_edit'] = True
            elif strain:
                context['user_strain_edit'] = (strain.added_by.id == user.id)
            
            if user.has_perm('strainbrowser.strain.delete'):
                context['user_strain_delete'] = True
        
        return context
    # _get_strain_context()
    
    context = functions.get_sidebar_context(user)
    context.update(_get_breeder_context(user=user,breeder=breeder))
    context.update(_get_strain_context(user=user,breeder=breeder,strain=strain))
    
    return context
# get_context_variables()

   
def export_breeder(user,breeders,domain,compression='none',valid=3600):
    def timestring(dt):
        return dt.strftime("%Y%m%d-%H%M%S")
    # timestring()

    now = datetime.datetime.now()
    
    xml_context = {
        'domain': domain,
        'breeders': breeders,
        'protocol': settings.SITE_PROTOCOL,
    }
    if compression not in COMPRESSION:
        compression = 'none'
    compress = COMPRESSION[compression]
    
    ofile_name = os.path.join(
        settings.MEDIA_ROOT,
        'export',
        'breeder',
        '.'.join((user.id,timestring(now),'breeder')))
        
    if 'extension' in compress:
        ofile_name = '.'.join((ofile_name,compress['extension']))
            
    data = render_to_string('strainbrowser/breeder/export.xml',xml_context)
    if compress['binfmt']:
        data = data.encode(encoding='UTF-8')
            
    with compress['open-func'](ofile_name,**compress['kwargs-write']) as ofile:
        ofile.write(data)
        
    FileValid.objects.create(filename=ofile_name,valid_until=(now + datetime.timedelta(valid)))
# export_breeder()

def import_breeder(self):
    pass


