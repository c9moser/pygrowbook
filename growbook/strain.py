# -*- coding: utf-8 -*-
# growbook/strain.py
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
from gi.repository import Gtk,Pango,Gdk
import os
import i18n; _=i18n.gettext

(STRAIN_UI,)=(os.path.join(os.path.dirname(__file__),'strain.ui'),)

class NewBreederDialogHandle(object):
    def __init__(self,parent,dbcon,id=0):
        object.__init__(self)
        self.dbcon=dbcon

        builder=Gtk.Builder()
        builder.add_objects_from_file(STRAIN_UI,('NewBreederDialog',))
        self.dialog=builder.get_object('NewBreederDialog')
        self.dialog.handler=self
        self.dialog.set_title(_("GrowBook: New Breeder"))
        if isinstance(parent,Gtk.Window):
            self.dialog.set_transient_for(parent)
        self.dialog.name_entry=builder.get_object('entry1')
        self.dialog.id_label=builder.get_object('label4')
        self.dialog.homepage_entry=builder.get_object('entry2')

        if id == 0:
            self.dialog.id_label.set_text(str(0))
        else:
            cursor=dbcon.cursor()
            cursor.execute('SELECT id,breeder,homepage FROM breeder WHERE id=?;',(id,))
            row=cursor.fetchone()
            self.dialog.id_label.set_text(str(row[0]))
            self.dialog.name_entry.set_text(row[1])
            self.dialog.homepage_entry.set_text(row[2])

        builder.connect_signals(self)

    def on_apply_clicked(self,button):
        cursor=self.dbcon.cursor()

        name=self.dialog.name_entry.get_text()
        homepage=self.dialog.homepage_entry.get_text()
        try:
            if int(self.dialog.id_label.get_text()) == 0:
                cursor.execute('INSERT INTO breeder (name,homepage) VALUES (?,?);',
                               (name,homepage))
            else:
                cursor.execute('UPDATE breeder SET name=?,homepage=? WHERE id=?;',
                               (name,homepage,int(self.id_label.get_text())))
            self.dbcon.commit()
        except Exception as ex:
            dialog=Gtk.MessageDialog(self.dialog,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=str(ex))
            dialog.run()
        

        
    def on_cancel_clicked(self,button):
        self.dialog.hide()

    def on_destroy(self,dialog=None):
        self.dialog.handler=None
        self.dialog=None
        

def NewBreederDialog(parent,dbcon,id=0):
    handler=NewBreederDialogHandle(parent,dbcon,id)
    return handler.dialog


class EditBreederDialogHandle(object):
    def __init__(self,parent,dbcon,id):
        object.__init__(self)
        self.dbcon=dbcon
        builder=Gtk.Builder()
        builder.add_objects_from_file(STRAIN_UI,('EditBreederDialog',))
        self.dialog=builder.get_object('EditBreederDialog')
        self.dialog.handler=self
        self.dialog.set_title(_("GrowBook: Edit Breeder"))
        builder.connect_signals(self)

        self.dialog.id_label=builder.get_object('label9')
        self.dialog.name_entry=builder.get_object('entry3')
        self.dialog.homepage_entry=builder.get_object('entry4')
        self.dialog.add_strain_button=builder.get_object('toolbutton1')
        self.dialog.edit_strain_button=builder.get_object('toolbutton2')
        self.dialog.remove_strain_button=builder.get_object('toolbutton3')
        self.dialog.strain_view=builder.get_object('treeview1')

        selection=self.dialog.strain_view.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        selection.connect('changed',self.on_strain_selection_changed)
        
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn('Name',renderer,text=1)
        self.dialog.strain_view.append_column(column)
        
        cursor=self.dbcon.cursor()
        cursor.execute('SELECT name,homepage FROM breeder WHERE id=?',(id,))
        row=cursor.fetchone()
        
        self.dialog.id_label.set_text(str(id))
        self.dialog.name_entry.set_text(row[0])
        self.dialog.homepage_entry.set_text(row[1])
        self.dialog.strain_view.set_model(self.__init_model())
        self.dialog.set_transient_for(parent)
        self.dialog.set_default_size(400,500)
        self.dialog.connect('destroy',self.on_destroy)
        self.dialog.show_all()
        
    def __init_model(self):
        model=Gtk.ListStore(int,str)

        cursor=self.dbcon.cursor()
        cursor.execute('SELECT id,name FROM strain WHERE breeder=? ORDER BY name;',
                       (int(self.dialog.id_label.get_text()),))
        for row in cursor:
            model.append((row[0],row[1]))
            
        return model

    def refresh_strains(self):
        self.dialog.strain_view.set_model(self.__init_model())
        self.dialog.strain_view.show()

    def on_strain_selection_changed(self,selection):
        pass
        
    def on_destroy(self,dialog=None):
        self.dialog.handler=None
        self.dialog=None
        
    def on_apply_clicked(self,button):
        cursor=self.dbcon.cursor()
        name=self.dialog.name_entry.get_text()
        homepage=self.dialog.homepage_entry.get_text()
        id=int(self.dialog.id_label.get_text())
        try:
            cursor.execute('UPDATE breeder SET name=?,homepage=? WHERE id=?;',
                           (name,homepage,id))
            self.dbcon.commit()
        except Exception as ex:
            dialog=Gtk.MessageDialog(self.dialog,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=str(ex))

            dialog.run()
            dialog.hide()
            dialog.destroy()
            
    def on_add_strain_clicked(self,toolbutton):
        dialog=StrainDialog(self.dialog,
                            self.dbcon,
                            breeder_id=int(self.dialog.id_label.get_text()))
        result=dialog.run()
        if result == Gtk.ResponseType.APPLY:
            self.refresh_strains()
        dialog.hide()
        dialog.destroy()

    def on_edit_strain_clicked(self,toolbutton):
        selection=self.dialog.strain_view.get_selection()
        model,iter=selection.get_selected()
        row=model[iter]
        dialog=StrainDialog(self.dialog,self.dbcon,id=row[0])
        result=dialog.run()
        if result == Gtk.ResponseType.APPLY:
            self.refresh_strains()
        dialog.hide()
        dialog.destroy()
       
    def on_remove_strain_clicked(self,toolbutton):
        model,iter=self.dialog.strain_view.get_selection().get_selected()
        if model and iter:
            dialog=Gtk.MessageDialog(self.dialog,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.WARNING,
                                     buttons=Gtk.ButtonsType.YES_NO,
                                     message_format=_("Do you really want to delete Strain '{0}'?").format(model[iter][1]))
            result=dialog.run()
            dialog.hide()
            if result==Gtk.ResponseType.YES:
                try:
                    self.dbcon.execute("DELETE FROM strain WHERE id=?;",(model[iter][0],))
                    self.dbcon.commit()
                except Exception as ex:
                    dialog2=Gtk.MessageDialog(self.dialog,
                                              flags=Gtk.DialogFlags.MODAL,
                                              message_type=Gtk.MessageType.WARNING,
                                              buttons=Gtk.ButtonsType.OK,
                                              message_format=str(ex))
                    dialog2.hide()
                    dialog2.destroy()
            dialog.destroy()
            self.refresh_strains()          
            
def EditBreederDialog(parent,dbcon,id):
    handler=EditBreederDialogHandle(parent,dbcon,id)
    return handler.dialog



class StrainDialogHandle(object):
    def __init__(self,parent,dbcon,id=0,breeder_id=0):
        object.__init__(self)
        builder=Gtk.Builder()
        builder.add_objects_from_file(STRAIN_UI,('EditStrainDialog',))

        self.dbcon=dbcon
        self.dialog=builder.get_object('EditStrainDialog')
        self.dialog.handler=self
        self.dialog.set_title("GrowBook: Strain")
        self.dialog.connect('destroy',self.on_destroy)
        self.dialog.id_label=builder.get_object('label18')
        self.dialog.breeder_label=builder.get_object('label12')
        self.dialog.id_label.set_text(str(id))
        self.dialog.name_entry=builder.get_object('entry5')
        self.dialog.homepage_entry=builder.get_object('entry6')
        self.dialog.seedfinder_entry=builder.get_object('entry7')
        self.dialog.info_view=builder.get_object('textview1')
        self.dialog.description_view=builder.get_object('textview2')

        self.dialog.set_transient_for(parent)
        
        cursor=self.dbcon.cursor()
        if id:
            cursor.execute('SELECT breeder,name,homepage,seedfinder,info,description FROM strain WHERE id=?;', (id,))
            row=cursor.fetchone()
            self.dialog.breeder_id=row[0]
            self.dialog.name_entry.set_text(row[1])
            self.dialog.homepage_entry.set_text(row[2])
            self.dialog.seedfinder_entry.set_text(row[3])

            buffer=self.dialog.info_view.get_buffer()
            buffer.set_text(row[4])

            buffer=self.dialog.description_view.get_buffer()
            buffer.set_text(row[5])

            cursor.execute('SELECT name FROM breeder WHERE id=?;',
                           (self.dialog.breeder_id,))
            row=cursor.fetchone()
            self.dialog.breeder_label.set_text(row[0])
            
        elif breeder_id:
            self.dialog.breeder_id=breeder_id
            cursor.execute('SELECT name FROM breeder WHERE id=?;',
                           (self.dialog.breeder_id,))
            row=cursor.fetchone()
            self.dialog.breeder_label.set_text(row[0])
        else:
            raise AttributeError(_("Attribute 'id' and 'breeder_id' not set!"))

        builder.connect_signals(self)
        self.dialog.show_all()

    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None

    def on_apply_clicked(self,button):
        cursor=self.dbcon.cursor()
        info_buffer=self.dialog.info_view.get_buffer()
        desc_buffer=self.dialog.description_view.get_buffer()

        try:
            if int(self.dialog.id_label.get_text()) == 0:
            
                cursor.execute('INSERT INTO strain (breeder,name,homepage,seedfinder,info,description) VALUES (?,?,?,?,?,?);',
                               (self.dialog.breeder_id,
                                self.dialog.name_entry.get_text(),
                                self.dialog.homepage_entry.get_text(),
                                self.dialog.seedfinder_entry.get_text(),
                                info_buffer.get_text(info_buffer.get_start_iter(),
                                                     info_buffer.get_end_iter(),
                                                     False),
                                desc_buffer.get_text(desc_buffer.get_start_iter(),
                                                      desc_buffer.get_end_iter(),
                                                      False)))
            else:
                cursor.execute('UPDATE strain SET name=?,homepage=?,seedfinder=?,info=?,description=? WHERE id=?;',
                               (self.dialog.name_entry.get_text(),
                                self.dialog.homepage_entry.get_text(),
                                self.dialog.seedfinder_entry.get_text(),
                                info_buffer.get_text(info_buffer.get_start_iter(),
                                                     info_buffer.get_end_iter(),
                                                     False),
                                desc_buffer.get_text(desc_buffer.get_start_iter(),
                                                     desc_buffer.get_end_iter(),
                                                     False),
                                int(self.dialog.id_label.get_text())))
            self.dbcon.commit()
        except Exception as ex:
            dialog=Gtk.MessageDialog(self.dialog,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=str(ex))
            dialog.run()
            dialog.hide()
            dialog.destroy()
        
            
def StrainDialog(parent,dbcon,id=0,breeder_id=0):
    handler=StrainDialogHandle(parent,dbcon,id,breeder_id)
    return handler.dialog

class StrainChooserDialogHandle(object):
    def __init__(self,parent,dbcon):
        object.__init__(self)

        self.dbcon=dbcon
        
        builder=Gtk.Builder()
        builder.add_objects_from_file(STRAIN_UI,('StrainChooserDialog',))
        self.dialog=builder.get_object('StrainChooserDialog')
        self.dialog.handler=self
        self.dialog.set_title(_("GrowBook: StrainChooser"))
        self.dialog.set_transient_for(parent)
        self.dialog.treeview=builder.get_object('treeview2')
        self.dialog.treeview.set_model(self.__create_model())

        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Name"),renderer,text=2)
        self.dialog.treeview.append_column(column)

        self.dialog.set_default_size(400,400)

        self.dialog.show_all()
        
    def __create_model(self):
        model=Gtk.TreeStore(int,int,str)

        cursor=self.dbcon.execute('SELECT id,name FROM breeder ORDER BY name;')
        for row in cursor:
            iter=model.append(None,(int(row[0]),0,row[1]))
            cursor2=self.dbcon.execute('SELECT id,name FROM strain WHERE breeder=? ORDER BY name;',(int(row[0]),))
            for row2 in cursor2:
                model.append(iter,(int(row[0]),int(row2[0]),row2[1]))
        return model


def StrainChooserDialog(parent,dbcon):
    handler=StrainChooserDialogHandle(parent,dbcon)
    return handler.dialog


class StrainView(Gtk.Box):
    (type,)=('StrainView',)
    def __init__(self,dbcon,id):
        Gtk.Box.__init__(self,orientation=Gtk.Orientation.VERTICAL)
        self.id=id

        self.breeder_homepage=''
        self.homepage=''
        self.seedfinder=''
        
        self.toolbar=Gtk.Toolbar()
        self.toolbar.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)

        self.breeder_homepage_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_HOME)
        self.breeder_homepage_toolbutton.connect('clicked',self.on_breeder_homepage_clicked)
        self.toolbar.insert(self.breeder_homepage_toolbutton,-1)

        separator=Gtk.SeparatorToolItem()
        self.toolbar.insert(separator,-1)
        
        self.seedfinder_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_FILE)
        self.seedfinder_toolbutton.connect('clicked', self.on_seedfinder_clicked)
        self.toolbar.insert(self.seedfinder_toolbutton,-1)

        self.homepage_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_HOME)
        self.homepage_toolbutton.connect('clicked', self.on_homepage_clicked)
        self.toolbar.insert(self.homepage_toolbutton,-1)

        separator=Gtk.SeparatorToolItem()
        self.toolbar.insert(separator,-1)
        
        self.refresh_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_REFRESH)
        self.refresh_toolbutton.connect('clicked', self.on_refresh_clicked)
        self.toolbar.insert(self.refresh_toolbutton,-1)
        
        self.pack_start(self.toolbar,False,False,0)
        
        self.scrolled_window=Gtk.ScrolledWindow()
        
        self.view=Gtk.TextView()
        self.view.set_editable(False)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD)
        
        cursor=dbcon.cursor()
        cursor.execute('SELECT name FROM strain WHERE id=?;',(self.id,))
        row=cursor.fetchone()
        self.title_label=Gtk.Label(row[0])
        
        self.scrolled_window.add(self.view)
        self.pack_start(self.scrolled_window,True,True,0)

        self.refresh(dbcon)

    def on_seedfinder_clicked(self,toolbutton):
        if self.seedfinder:
            os.startfile(self.seedfinder)

    def on_homepage_clicked(self,toolbutton):
        if self.homepage:
            os.startfile(self.homepage)
            
    def on_breeder_homepage_clicked(self,toolbutton):
        if self.breeder_homepage:
            os.startfile(self.breeder_homepage)

    def on_refresh_clicked(self,toolbutton):
        self.refresh(self.get_toplevel().dbcon)
           
    def refresh(self,dbcon):
        self.view.set_editable(True)
        buffer=Gtk.TextBuffer.new()
        
        cursor=dbcon.cursor()
        cursor.execute('SELECT id,breeder,name,homepage,seedfinder,info,description FROM strain WHERE id=?;',(self.id,))
        row=cursor.fetchone()

        self.homepage=row[3]
        self.seedfinder=row[4]
        
        if self.homepage:
            self.homepage_toolbutton.set_sensitive(True)
        else:
            self.homepage_toolbutton.set_sensitive(False)

        if self.seedfinder:
            self.seedfinder_toolbutton.set_sensitive(True)
        else:
            self.seedfinder_toolbutton.set_sensitive(False)
            
        cursor.execute('SELECT id,name,homepage FROM breeder WHERE id=?;',(row[1],))
        row2=cursor.fetchone()

        self.breeder_homepage=row2[2]
        if self.breeder_homepage:
            self.breeder_homepage_toolbutton.set_sensitive(True)
        else:
            self.breeder_homepage_toolbutton.set_sensitive(False)

        tagtable=buffer.get_tag_table()
        tag=Gtk.TextTag.new('H1')
        tag.props.scale=3.0
        tag.props.weight=Pango.Weight.BOLD
        tagtable.add(tag)
        buffer.insert_with_tags(buffer.get_start_iter(),
                                '{0} - {1}\n'.format(row2[1],row[2]),
                                tag)

        tag=Gtk.TextTag.new('H2')
        tag.props.scale=1.5
        tag.props.weight=Pango.Weight.BOLD
        tagtable.add(tag)
        buffer.insert_with_tags(buffer.get_end_iter(),'\n'+_('Homepage')+'\n',tag)
        buffer.insert(buffer.get_end_iter(),'{0}\n'.format(row[3]))

        buffer.insert_with_tags(buffer.get_end_iter(),'\n'+_('Seedfinder.eu')+'\n',tag)
        buffer.insert(buffer.get_end_iter(),'{0}\n'.format(row[4]))
        
        buffer.insert_with_tags(buffer.get_end_iter(),'\n'+_('Info')+'\n',tag)
        buffer.insert(buffer.get_end_iter(),'{0}\n'.format(row[5]))
        
        buffer.insert_with_tags(buffer.get_end_iter(),'\n'+'Description'+'\n',tag)
        buffer.insert(buffer.get_end_iter(),'{0}\n'.format(row[6]))

        self.view.set_buffer(buffer)
        self.view.set_editable(False)
        

class StrainSelector(Gtk.ScrolledWindow):
    def __init__(self,dbcon):
        Gtk.ScrolledWindow.__init__(self)
        
        self.treeview=Gtk.TreeView(self.__init_model(dbcon))
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Name"),renderer,text=2)
        self.treeview.append_column(column)
        self.treeview.connect('row_activated',self.on_row_activated)
        self.treeview.connect('button-press-event',self.on_treeview_button_press_event)
        self.add(self.treeview)
        
    def __init_model(self,dbcon):
        model=Gtk.TreeStore(int,int,str)

        cursor=dbcon.cursor()
        cursor2=dbcon.cursor()
        cursor.execute('SELECT id,name FROM breeder ORDER BY name;')
        for row in cursor:
            breeder_id=int(row[0])
            iter=model.append(None,[breeder_id,0,row[1]])
            
            cursor2.execute('SELECT id,name FROM strain WHERE breeder=? ORDER BY name;',(row[0],))
            for row2 in cursor2:
                model.append(iter,[breeder_id,int(row2[0] or 0),row2[1]])
        
        return model

    def refresh(self,dbcon):
        self.treeview.set_model(self.__init_model(dbcon))
        self.show()

    def on_treeview_button_press_event(self,treeview,event):
        if event.button == 3 and event.type==Gdk.EventType.BUTTON_PRESS:
            #show context menu
            window=self.get_toplevel()
            window.strain_selector_popup.popup(None,
                                               None,
                                               None,
                                               None,
                                               event.button,
                                               event.time)
    
    def on_row_activated(self,treeview,path,column):
        window=self.get_toplevel()
        model=self.treeview.get_model()
        iter=model.get_iter(path)
        row=model[iter]
        if row[1]:
            strain_view=StrainView(window.dbcon,row[1])
            window.add_browser_page(strain_view)
            window.show_all()

    def edit_selected_breeder(self,dbcon):
        model,iter=self.treeview.get_selection().get_selected()
        
        if model and iter:
            window=self.get_toplevel()
            row=model[iter]
            dialog=EditBreederDialog(window,window.dbcon,row[0])

            result=dialog.run()

            self.refresh(dbcon)
            dialog.hide()
            dialog.destroy()

    def delete_selected_breeder(self,dbcon):
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter and model[iter][0]:
            cursor=dbcon.execute("SELECT name from breeder WHERE id=?;",
                                 (model[iter][0],))
            row=cursor.fetchone()
            window=self.get_toplevel()
            dialog=Gtk.MessageDialog(parent=window,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.WARNING,
                                     buttons=Gtk.ButtonsType.YES_NO)
            dialog.set_markup(_("This deletes breeder '{0}' and all corresponding strains.\nDo you want to proceed?").format(row[0]))
            
            result=dialog.run()
            if result==Gtk.ResponseType.YES:
                try:
                    dbcon.execute("DELETE FROM strain WHERE breeder=?;",
                                  (model[iter][0],))
                    dbcon.execute("DELETE FROM breeder WHERE id=?;",
                                  (model[iter][0],))
                    dbcon.commit()
                except:
                    dialog=Gtk.MessageDialog(self.get_toplevel(),
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=str(ex))
                    dialog.run()
                    dialog.hide()
                    dialog.destroy()
                self.refresh(dbcon)
            dialog.hide()
            dialog.destroy()

    def add_strain(self,dbcon):
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter and model[iter][0]:
            window=self.get_toplevel()
            dialog=StrainDialog(window,dbcon,breeder_id=model[iter][0])
            result=dialog.run()

            if result==Gtk.ResponseType.APPLY:
                self.refresh(dbcon)

            dialog.hide()
            dialog.destroy()
            
    def edit_selected_strain(self,dbcon):
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter and model[iter][1]:
            window=self.get_toplevel()
            row=model[iter]
            dialog=StrainDialog(window,window.dbcon,row[1])

            result=dialog.run()
            if result == Gtk.ResponseType.APPLY:
                self.refresh(dbcon)


            dialog.hide()
            dialog.destroy()

    def delete_selected_strain(self,dbcon):
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter and model[iter][1]:
            window=self.get_toplevel()
            cursor=dbcon.execute("SELECT name FROM breeder WHERE id=?;",
                                 (model[iter][0],))
            row=cursor.fetchone()
            dialog=Gtk.MessageDialog(parent=window,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.WARNING,
                                     buttons=Gtk.ButtonsType.YES_NO)
            dialog.set_markup(_("This deletes strain '{0}' from '{1}'.\nDo you want to proceed?").format(model[iter][2],row[0]))
            result=dialog.run()
            if result == Gtk.ResponseType.YES:
                try:
                    dbcon.execute("DELETE FROM strain WHERE id=?;",
                                  (model[iter][1],))
                    dbcon.commit()
                except:
                    dialog=Gtk.MessageDialog(self.dialog,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.ERROR,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=str(ex))
                    dialog.run()
                    dialog.hide()
                    dialog.destroy()
                self.refresh(dbcon)
            dialog.hide()
            dialog.destroy()

