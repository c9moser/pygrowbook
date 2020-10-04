# growbook/app.py
################################################################################
# Copyright (C) 2020  Christian Moser                                          #
#                                                                              #
#   This program is free software: you can redistribute it and/or modify       #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
################################################################################

import gi
from gi.repository import Gtk, Gio, GLib
import sqlite3
import os
import config
import growlog
import strain
import about
import i18n

_=i18n.gettext

class AppWindowHandle(object):
    def __init__(self):
        if not os.path.exists(config.config['dbfile']):
            os.makedirs(config.config['datadir'])
            self.dbcon=sqlite3.connect(config.config['dbfile'])
            self.dbcon.text_factory=str
            with open(os.path.join(os.path.dirname(__file__),'growbook.sql'),'r') as f:
                sql=f.read()
                self.dbcon.executescript(sql)
        else:
            self.dbcon=sqlite3.connect(config.config['dbfile'])
            self.dbcon.text_factory=str
            
        builder=Gtk.Builder.new_from_file(os.path.join(os.path.dirname(__file__),'appwindow.ui'))
        builder.connect_signals(self)
        self.window=builder.get_object('window1')
        self.window.set_title('GrowBook')
        self.window.dbcon=self.dbcon
        self.window.handler=self
        self.window.dbcon=self.dbcon
        paned=builder.get_object('paned1')

        self.window.selector=Gtk.Notebook()
        self.window.selector.set_scrollable(True)
        label=Gtk.Label(_('GrowLog'))
        self.window.growlog_selector=growlog.GrowlogSelector(self.dbcon)
        self.window.selector.append_page(self.window.growlog_selector,label)

        label=Gtk.Label(_('Strains'))
        self.window.strain_selector=strain.StrainSelector(self.dbcon)
        self.window.selector.append_page(self.window.strain_selector,label)

        paned.add1(self.window.selector)

    
        self.window.browser=Gtk.Notebook()
        self.window.browser.set_scrollable(True)
        paned.add2(self.window.browser)

        self.window.set_default_size(800,600)
        self.window.connect('destroy',self.on_destroy)
        
        self.window.add_browser_page=self.add_browser_page
        self.window.growlog_selector_popup=builder.get_object("GrowlogSelectorPopup")
        self.window.strain_selector_popup=builder.get_object("StrainSelectorPopup")
        self.window.growlog_entry_popup=builder.get_object("GrowlogEntryPopup")

        if config.config['open-ongoing-growlogs']:
            self.window.growlog_selector.open_ongoing_growlogs(self.dbcon)
            
        self.window.show_all()
        
    def add_browser_page(self,child):
        for pageno in xrange(self.window.browser.get_n_pages()):
            page=self.window.browser.get_nth_page(pageno)
            
            if page.type==child.type and page.id==child.id:
                self.window.browser.set_current_page(pageno)
                page.refresh(self.dbcon)
                return

        def on_title_close(button,widget):
            pageno=self.window.browser.page_num(child)
            self.window.browser.remove_page(pageno)

        hbox=Gtk.HBox()
        hbox.pack_start(child.title_label,False,False,0)

        close_image=Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE,Gtk.IconSize.MENU)
        button=Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(close_image)
        #style=Gtk.RcStyle()
        #style.xthickness=0
        #style.ythickness=0
        #button.modify_style(style)
        button.connect('clicked',on_title_close,child)
        hbox.pack_start(button,False,False,0)

        hbox.show_all()
        child.show()
        self.window.browser.append_page(child,hbox)
        self.window.browser.set_current_page(-1)
        self.window.browser.show()
        

    def on_action_edit_growlog_entry(self,action):
        pageno=self.window.browser.get_current_page()
        if (pageno >= 0):
            child=self.window.browser.get_nth_page(pageno)
        if child and child.type=='Growlog':
            model,iter=child.treeview.get_selection().get_selected()
            if model and iter:
                dialog=growlog.GrowlogEntryDialog(self.window,self.dbcon,model[iter][0])
                result=dialog.run()
                if result==Gtk.ResponseType.APPLY:
                    child.refresh(self.dbcon)
                dialog.hide()
                dialog.destroy()
        
    def on_action_quit(self,action):
        self.window.hide()
        self.window.destroy()

    
    def on_action_new_breeder(self,action):
        dialog=strain.NewBreederDialog(self.window, self.dbcon)
        dialog.show_all()
        result=dialog.run()
        if result==Gtk.ResponseType.APPLY:
            #recreate table
            self.window.strain_selector.refresh(self.dbcon)
            cursor=self.dbcon.cursor()
            cursor.execute('SELECT id FROM breeder WHERE name=?;',
                           (dialog.name_entry.get_text(),))
            row=cursor.fetchone()
            dialog.hide()
            dialog2=strain.EditBreederDialog(self.window,self.dbcon,row[0])
            result2=dialog2.run()
            if result2 == Gtk.ResponseType.APPLY:
                pass
                
            dialog2.hide()
            dialog2.destroy()
            dialog.destroy()
            self.window.strain_selector.refresh(self.dbcon)
        else:
            dialog.hide()
            dialog.destroy()

    def on_action_selector_edit_breeder(self,action):
        self.window.strain_selector.edit_selected_breeder(self.dbcon)

    def on_action_selector_delete_breeder(self,action):
        self.window.strain_selector.delete_selected_breeder(self.dbcon)

    def on_action_selector_add_strain(self,action):
        self.window.strain_selector.add_strain(self.dbcon)
        
    def on_action_selector_edit_strain(self,action):
        self.window.strain_selector.edit_selected_strain(self.dbcon)

    def on_action_selector_delete_strain(self,action):
        self.window.strain_selector.delete_selected_strain(self.dbcon)

    def on_action_selector_edit_growlog(self,action):
        self.window.growlog_selector.edit_selected_growlog(self.dbcon)

    def on_action_selector_open_growlog(self,action):
        self.window.growlog_selector.open_selected_growlog(self.dbcon)

    def on_action_selector_delete_growlog(self,action):
        self.window.growlog_selector.delete_selected_growlog(self.dbcon)
        
    def on_action_edit_breeder(self,action):
        pageno=self.window.browser.get_current_page()
        if (pageno >= 0):
            child=self.window.browser.get_nth_page(pageno)
        else:
            child=None
            
        if child and child.type=='StrainView':
            cursor=self.dbcon.execute('SELECT id,breeder FROM strain WHERE id=?;',
                                      (child.id,))
            row=cursor.fetchone()
            dialog=strain.EditBreederDialog(self.window,self.dbcon,row[1])
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                pass
            dialog.hide()
            dialog.destroy()
            child.refresh(self.dbcon)
            child.show()
            
    def on_action_edit_strain(self,action):
        pageno=self.window.browser.get_current_page()
        if pageno >= 0:
            child=self.window.browser.get_nth_page(pageno)
        else:
            child=None
            
        if child and child.type=='StrainView':
            dialog=strain.StrainDialog(self.window,self.dbcon,child.id)
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                child.refresh(self.dbcon)
                child.show()
            dialog.hide()
            dialog.destroy()
            
    def on_action_new_growlog(self,action):
        dialog=growlog.NewGrowlogDialog(self.window,self.dbcon)
        result=dialog.run()
        if result==Gtk.ResponseType.APPLY:
            dialog.hide()
            cursor=self.dbcon.cursor()
            cursor.execute('SELECT id FROM growlog WHERE title=?',
                           (dialog.title_entry.get_text(),))
            row=cursor.fetchone()
            if row:
                dialog2=growlog.EditGrowlogDialog(self.window,self.dbcon,row[0])
                result2=dialog2.run()

                if result2 == Gtk.ResponseType.APPLY:
                    pass
                dialog2.hide()
                dialog2.destroy()
            
                self.window.growlog_selector.refresh(self.dbcon)
                page=growlog.GrowlogView(self.dbcon,row[0])
                self.add_browser_page(page)
        else:
            dialog.hide()
        dialog.destroy()
        

    def on_action_new_growlog_entry(self,action):
        pageno=self.window.browser.get_current_page()
        if pageno >= 0:
            child=self.window.browser.get_nth_page(pageno)
        else:
            child=None

        if child and child.type == 'Growlog':
            dialog=growlog.GrowlogEntryDialog(self.window,
                                              self.dbcon,
                                              growlog_id=child.id)
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                child.refresh(self.dbcon)
            dialog.hide()
            dialog.destroy()
            
    def on_action_delete_growlog_entry(self,action):
        pageno=self.window.browser.get_current_page()
        if pageno >= 0:
            child=self.window.browser.get_nth_page(pageno)
        else:
            child=None

        if child and child.type == 'Growlog':
            child.on_action_growlog_entry_delete(action)
            
    def on_action_edit_growlog(self,action):
        pageno=self.window.browser.get_current_page()
        if pageno >= 0:
            child=self.window.browser.get_nth_page(pageno)
        else:
            child=None

        if child and child.type == 'Growlog':
            dialog = growlog.EditGrowlogDialog(self.window,self.dbcon,child.id)
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                child.refresh(self.dbcon)
            dialog.hide()
            dialog.destroy()
    
    def on_action_about(self,action):
        dialog=about.AboutDialog(self.window)
        dialog.run()
        dialog.hide()
        dialog.destroy()

    def on_action_close(self,action):
        pageno=self.window.browser.get_current_page()
        if pageno >= 0:
            self.window.browser.remove_page(pageno)
            self.window.browser.show()
    
    def on_destroy(self,window):
        self.window.handler=None
        self.window=None
        self.dbcon.close()
        Gtk.main_quit()

def AppWindow():
    handler=AppWindowHandle()
    return handler.window
    
