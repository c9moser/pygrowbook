from main import functions

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
