#-*- coding:utf-8 -*-

def growlog_image_upload_path(instance,filename):
    return "growlog/{0}/{1}".format(instance.entry.growlog.id,filename)
    
