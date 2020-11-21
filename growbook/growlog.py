# -*- coding: utf-8 -*-
# growbook/growlog.py
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
from gi.repository import Gtk,Pango,Gdk,GdkPixbuf
import sqlite3
import os
import datetime
from . import strain 
from . import i18n; _=i18n.gettext
from . import tools
import growbook
from collections import namedtuple

(
    GROWLOG_UI,
    FLOWER_ICON
)=(
    os.path.join(os.path.dirname(__file__),'growlog.ui'),
    os.path.join(os.path.dirname(__file__),'flower-icon.svg')
)

class NewGrowlogDialogHandle(object):
    def __init__(self,parent,dbcon):
        object.__init__(self)
        self.dbcon=dbcon

        builder=Gtk.Builder()
        builder.add_objects_from_file(GROWLOG_UI,('NewGrowlogDialog',))
        builder.connect_signals(self)

        self.dialog=builder.get_object('NewGrowlogDialog')
        self.dialog.set_default_size(500,400)
        self.dialog.set_transient_for(parent)
        self.dialog.set_title(_('GrowBook: New Growlog'))
        
        self.dialog.id_label=builder.get_object('label13')
        self.dialog.title_entry=builder.get_object('entry2')
        self.dialog.description_view=builder.get_object('textview2')

        self.dialog.id_label.set_text(str(0))

    def on_apply_clicked(self,button):
        buffer=self.dialog.description_view.get_buffer()
        timestamp=datetime.datetime.now()
        
        cursor=self.dbcon.cursor()
        try:
            cursor.execute('INSERT INTO growlog (title,description,created_on) VALUES (?,?,?);',
                           (self.dialog.title_entry.get_text(),
                            buffer.get_text(buffer.get_start_iter(),
                                            buffer.get_end_iter(),
                                            False),
                            timestamp.strftime('%Y-%m-%d %H:%M:%S')))
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

    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None
        
def NewGrowlogDialog(parent,dbcon):
    handler=NewGrowlogDialogHandle(parent,dbcon)
    return handler.dialog

class EditGrowlogDialogHandle(object):
    (COL_ID,COL_STRAIN_ID,COL_BREEDER,COL_STRAIN)=range(4)
    def __init__(self,parent,dbcon,id):
        object.__init__(self)

        self.dbcon=dbcon
        self.id=id
        builder=Gtk.Builder()
        builder.add_objects_from_file(GROWLOG_UI,('EditGrowlogDialog',))
        builder.connect_signals(self)
        
        self.dialog=builder.get_object('EditGrowlogDialog')
        self.dialog.handler=self
        self.dialog.set_transient_for(parent)
        self.dialog.set_default_size(500,400)
        self.dialog.set_title(_('GrowBook: Edit Growlog'))
        
        self.dialog.id_label=builder.get_object('label7')
        self.dialog.created_on_label=builder.get_object('label9')
        self.dialog.finished_on_label=builder.get_object('label10')
        self.dialog.title_entry=builder.get_object('entry1')
        self.dialog.description_view=builder.get_object('textview1')
        self.dialog.strain_view=builder.get_object('treeview1')
        cursor=self.dbcon.execute('SELECT id,title,created_on,finished_on,description FROM growlog WHERE id=?',
                                  (id,))
                                  
        row=cursor.fetchone()
        self.dialog.id_label.set_text(str(row[0]))
        self.dialog.title_entry.set_text(row[1])
        self.dialog.created_on_label.set_text(row[2])
        self.dialog.finished_on_label.set_text(row[3])
        buffer=self.dialog.description_view.get_buffer()
        buffer.set_text(row[4])
        self.dialog.show_all()

        self.dialog.strain_view.set_model(self.__create_strainview_model(self.dbcon))
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Breeder"),renderer,text=3)
        self.dialog.strain_view.append_column(column)

        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Strain"),renderer,text=4)
        self.dialog.strain_view.append_column(column)
        
        
    def __create_strainview_model(self,dbcon):
        model=Gtk.ListStore(int,int,int,str,str)
        cursor=self.dbcon.execute('SELECT id,growlog,strain FROM growlog_strain WHERE growlog=?;',
                                  (self.id,))
        for row in cursor:
            cursor2=self.dbcon.execute("SELECT breeder_name,name FROM strain_view WHERE id=?;",
                                       (int(row[2]),))
            row2=cursor2.fetchone()
            model.append((int(row[0]),int(row[1]),int(row[2]),row2[0] ,row2[1]))

        return model

    def on_apply_clicked(self,button):
        buffer=self.dialog.description_view.get_buffer()
        cursor=self.dbcon.cursor()
        try:
            cursor.execute("UPDATE growlog SET title=?,description=? WHERE id=?;",
                           (self.dialog.title_entry.get_text(),
                            buffer.get_text(buffer.get_start_iter(),buffer.get_end_iter(),False),
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
            
    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None

    def on_add_strain_clicked(self,toolbutton):
        dialog=strain.StrainChooserDialog(self.dialog,self.dbcon)
        result=dialog.run()
        if result==Gtk.ResponseType.APPLY:
            model,iter=dialog.treeview.get_selection().get_selected()
            if model and model[iter][1]:
                try:
                    self.dbcon.execute("INSERT INTO growlog_strain (growlog,strain) VALUES (?,?);", 
                                       (int(self.dialog.id_label.get_text()),
                                        model[iter][1]))
                    self.dbcon.commit()
                except Exception as ex:
                    dialog2=Gtk.MessageDialog(self.dialog,
                                              flags=Gtk.DialogFlags.MODAL,
                                              message_type=Gtk.MessageType.ERROR,
                                              buttons=Gtk.ButtonsType.OK,
                                              message_format=str(ex))
                    dialog2.run()
                    dialog2.hide()
                    dialog2.destroy()
            self.dialog.strain_view.set_model(self.__create_strainview_model(self.dbcon))
            self.dialog.strain_view.show()

        dialog.hide()
        dialog.destroy()
        
    def on_remove_strain_clicked(self,toolbutton):
        model,iter=self.dialog.strain_view.get_selection().get_selected()
        if model and model[iter][0]:
            try:
                self.dbcon.execute("DELETE FROM growlog_strain WHERE id=?;",
                                   (model[iter][0],))
                self.dialog.strain_view.set_model(self.__create_strainview_model(self.dbcon))
                self.dialog.strain_view.show()
            except Exception as ex:
                dialog=Gtk.MessageDialog(self.dialog,
                                         flags=Gtk.DialogFlags.MODAL,
                                         message_type=Gtk.MessageType.ERROR,
                                         buttons=Gtk.ButtonsType.OK,
                                         message_format=str(ex))
                dialog.run()

def EditGrowlogDialog(parent,dbcon,id):
    handler=EditGrowlogDialogHandle(parent,dbcon,id)
    return handler.dialog

class GrowlogEntryDialogHandle(object):
    def __init__(self,parent,dbcon,id=0,growlog_id=0):
        if not id and not growlog_id:
            raise AttributeError(_("'id' and 'growlog_id' not set!"))

        self.dbcon=dbcon
        if not growlog_id:
            cursor=self.dbcon.execute("SELECT growlog FROM growlog_entry WHERE id=?;", (id,))
            row=cursor.fetchone()
            self.growlog_id=int(row[0])
        else:  
            self.growlog_id=growlog_id
        self.id=id

        builder=Gtk.Builder()
        builder.add_objects_from_file(GROWLOG_UI,("GrowlogEntryDialog",))
        builder.connect_signals(self)
        
        self.dialog=builder.get_object("GrowlogEntryDialog")
        self.dialog.set_default_size(400,400)
        self.dialog.handler=self
        self.dialog.set_transient_for(parent)
        self.dialog.entry_view=builder.get_object('textview3')
        self.dialog.set_title(_('GrowBook: Growlog Entry'))
        if self.id:
            buffer=self.dialog.entry_view.get_buffer()
            cursor=self.dbcon.execute("SELECT entry FROM growlog_entry WHERE id=?;",(self.id,))
            row=cursor.fetchone()
            buffer.set_text(row[0])

        self.dialog.show_all()

    def on_destroy(self,dialog):
        self.dialog.handler=None
        self.dialog=None
        
    def on_apply_clicked(self,button):
        buffer=self.dialog.entry_view.get_buffer()
        try:
            if not self.id:
                timestamp=datetime.datetime.now()
                cursor=self.dbcon.execute('INSERT INTO growlog_entry (growlog,entry,created_on) VALUES (?,?,?);',
                                          (self.growlog_id,
                                           buffer.get_text(buffer.get_start_iter(),
                                                           buffer.get_end_iter(),
                                                           False),
                                           timestamp.strftime('%Y-%m-%d %H:%M:%S')))
            else:
                cursor=self.dbcon.execute('UPDATE growlog_entry SET entry=? WHERE id=?;', 
                                          (buffer.get_text(buffer.get_start_iter(),
                                                           buffer.get_end_iter(),
                                                           False),
                                           self.id))
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

def GrowlogEntryDialog(parent,dbcon,id=0,growlog_id=0):
    handler=GrowlogEntryDialogHandle(parent,dbcon,id,growlog_id)
    return handler.dialog                  

GrowlogCalendarEntry=namedtuple('GrowlogCalendarEntry','time entry')

class GrowlogCalendar(Gtk.Calendar):
    def __init__(self,dbcon,growlog_id):
        Gtk.Calendar.__init__(self)
        self.dbcon=dbcon
        self.id=growlog_id
        self.dates={}

        cursor=self.dbcon.execute("SELECT created_on,flower_on,finished_on FROM growlog WHERE id=?;",(self.id,))
        row=cursor.fetchone()
        date_str,time_str=row[0].split(' ')
        date=datetime.date(*tuple((int(i) for i in date_str.split('-'))))
        time=datetime.time(*tuple((int(i) for i in time_str.split(':'))))
        self.created_on=datetime.datetime(date.year,date.month,date.day,
                                          time.hour,time.minute,time.second)
        self.dates[date]=[GrowlogCalendarEntry(time,_("Grow started"))]
        if row[1]:
            self.flower_on=datetime.date(*tuple((int(i) for i in row[1].split('-'))))
            self.dates[self.flower_on]=[GrowlogCalendarEntry(datetime.time(0,0,0),_("Begin flowering"))]
        else:
            self.flower_on=None

        if row[2]:
            date_str,time_str=row[2].split(' ')
            date=datetime.date(*tuple((int(i) for i in date_str.split('-'))))
            time=datetime.time(*tuple((int(i) for i in time_str.split(':'))))
            self.finished_on=datetime.datetime(date.year,date.month,date.day,
                                               time.hour,time.minute,time.second)
            self.dates[date]=[GrowlogCalendarEntry(time,_("Finished grow."))]
        else:
            self.finished_on=None

        cursor=self.dbcon.execute("SELECT created_on,entry FROM growlog_entry WHERE growlog=? ORDER BY created_on;",(self.id,))
        for row in cursor:
            date_str,time_str=row[0].split(' ')
            date=datetime.date(*tuple((int(i) for i in date_str.split('-'))))
            time=datetime.time(*tuple((int(i) for i in time_str.split(':'))))
            if date in self.dates.keys():
                entry_inserted=False
                for i in range(len(self.dates[date])):
                    if self.dates[date][i].time > time:
                        self.dates[date].insert(i,GrowlogCalendarEntry(time,row[1]))
                        entry_inserted=True
                        break
                if not entry_inserted:
                    self.dates[date].append(GrowlogCalendarEntry(time,row[1]))
            else:
                self.dates[date]=[GrowlogCalendarEntry(time,row[1])]
                        
        self.select_month(self.created_on.month-1,self.created_on.year)
        self.select_day(self.created_on.day)
        self.do_month_changed()

    def do_day_selected(self):
        pass
    
    def do_month_changed(self):
        self.clear_marks()
        year,month,day=self.get_date()
        for date in self.dates.keys():
            if date.year==year and date.month==month+1:
                self.mark_day(date.day)


class GrowlogCalendarDialog(Gtk.Dialog):
    def __init__(self,parent,dbcon,growlog_id):
        Gtk.Dialog.__init__(self,title=_("Growlog Calendar"),parent=parent)
        self.set_default_size(600,400)
        self.dbcon=dbcon
        self.add_button("Close",Gtk.ResponseType.CLOSE)
        
        vbox=self.get_content_area()
        self.calendar=GrowlogCalendar(self.dbcon,growlog_id)
        self.calendar.connect("day-selected",self.on_calendar_day_selected)
        hbox=Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox.pack_start(self.calendar,False,False,0)
        vbox.pack_start(hbox,False,False,0)

        self.treeview=Gtk.TreeView.new_with_model(self.__create_model())

        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Time"),renderer,text=0)
        self.treeview.append_column(column)

        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Entry"),renderer,text=1)
        self.treeview.append_column(column)

        scrolled_window=Gtk.ScrolledWindow()
        scrolled_window.add(self.treeview)
        vbox.pack_start(scrolled_window,True,True,0)
        self.show_all()

    def __create_model(self):
        model=Gtk.ListStore(str,str)

        year,month,day=self.calendar.get_date()
        if self.calendar.get_day_is_marked(day):
            for entry in self.calendar.dates[datetime.date(year,month+1,day)]:
                model.append([entry.time.isoformat(),entry.entry])
        return model

    def on_calendar_day_selected(self,calendar):
        self.treeview.set_model(self.__create_model())
        self.treeview.show()
        
class GrowlogView(Gtk.Box):
    (type,)=('Growlog',)
    def __init__(self,dbcon,id):
        Gtk.Box.__init__(self,orientation=Gtk.Orientation.VERTICAL)
        self.id=id

        cursor=dbcon.execute("SELECT title,created_on,flower_on,finished_on FROM growlog WHERE id=?",(id,))
        row=cursor.fetchone()
        self.title_label=Gtk.Label(row[0])

        dtstr=row[1]
        datestr,timestr=tuple(row[1].split(" "))
        year,month,day=(int(i) for i in datestr.split("-"))
        hour,minute,second=(int(i) for i in timestr.split(':'))
        self.created_on=datetime.datetime(year,month,day,hour,minute,second)

        if row[2]:
            datestr=row[2]
            year,month,day=(int(i) for i in datestr.split('-'))
            self.flower_on=datetime.date(year,month,day)
        else:
            self.flower_on=None
        
        if row[3]:
            self.finished=True
            datestr,timestr=row[3].split(' ')
            year,month,day=(int(i) for i in datestr.split('-'))
            hour,minute,second=(int(i) for i in timestr.split(':'))
            self.finished_on=datetime.datetime(year,month,day,hour,minute,second)
        else:
            self.finished=False
            self.finished_on=None


        # Toolbar
        self.toolbar=Gtk.Toolbar()
        self.toolbar.set_icon_size(Gtk.IconSize.SMALL_TOOLBAR)
        
        self.edit_growlog_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_EDIT)
        self.edit_growlog_toolbutton.set_label(_("Edit Growlog"))
        self.edit_growlog_toolbutton.set_tooltip_text(_("Edit Growlog."))
        self.edit_growlog_toolbutton.connect('clicked',self.on_edit_growlog_clicked)
        self.toolbar.insert(self.edit_growlog_toolbutton,-1)

        valid,width,height=Gtk.icon_size_lookup(Gtk.IconSize.SMALL_TOOLBAR)
        pixbuf=GdkPixbuf.Pixbuf.new_from_file_at_scale(FLOWER_ICON,
                                                       width,
                                                       height,
                                                       False)
        image=Gtk.Image.new_from_pixbuf(pixbuf)
        self.flower_toolbutton=Gtk.ToolButton.new(image,_("Flowering"))
        self.flower_toolbutton.set_tooltip_text(_("Start flowering."))
        self.flower_toolbutton.connect('clicked',self.on_flower_clicked)
        if self.flower_on:
            self.flower_toolbutton.set_sensitive(False)
        self.toolbar.insert(self.flower_toolbutton,-1)

        self.finish_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_STOP)
        self.finish_toolbutton.set_tooltip_text(_("Finish Growlog"))
        self.finish_toolbutton.connect('clicked',self.on_finish_clicked)
        if self.finished:
            self.finish_toolbutton.set_sensitive(False)
            
        self.toolbar.insert(self.finish_toolbutton,-1)
        
        separator=Gtk.SeparatorToolItem.new()
        self.toolbar.insert(separator,-1)

        self.new_log_entry_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
        self.new_log_entry_toolbutton.connect('clicked',self.on_new_log_entry_clicked)
        self.new_log_entry_toolbutton.set_tooltip_text(_("New Growlog-entry."))
        if self.finished:
            self.new_log_entry_toolbutton.set_sensitive(False)
        self.toolbar.insert(self.new_log_entry_toolbutton,-1)

        #
        self.edit_log_entry_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_EDIT)
        self.edit_log_entry_toolbutton.set_tooltip_text(_("Edit selected Growlog-entry."))
        self.edit_log_entry_toolbutton.connect('clicked',self.on_edit_log_entry_clicked)
        self.edit_log_entry_toolbutton.set_sensitive(False)
        self.toolbar.insert(self.edit_log_entry_toolbutton,-1)

        self.remove_log_entry_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
        self.remove_log_entry_toolbutton.set_tooltip_text(_("Delete selected Growlog-entry."))
        self.remove_log_entry_toolbutton.connect('clicked',self.on_remove_log_entry_clicked)
        self.remove_log_entry_toolbutton.set_sensitive(False)
        self.toolbar.insert(self.remove_log_entry_toolbutton,-1)
        
        separator=Gtk.SeparatorToolItem()
        self.toolbar.insert(separator,-1)

        self.flowering_date_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_INFO)
        self.flowering_date_toolbutton.set_tooltip_text(_("Calculate end of flowering date."))
        self.flowering_date_toolbutton.connect('clicked',self.on_flowering_date_clicked)
        self.toolbar.insert(self.flowering_date_toolbutton,-1)

        self.growlog_calendar_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_JUMP_TO)
        self.growlog_calendar_toolbutton.set_tooltip_text(_("Growlog Calendar"))
        self.growlog_calendar_toolbutton.connect('clicked',self.on_growlog_calendar_clicked)
        self.toolbar.insert(self.growlog_calendar_toolbutton,-1)
        
        separator=Gtk.SeparatorToolItem()
        self.toolbar.insert(separator,-1)
        
        self.refresh_toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_REFRESH)
        self.refresh_toolbutton.set_tooltip_text(_("Refresh Grwolog."))
        self.refresh_toolbutton.connect("clicked",self.on_refresh_clicked)
        self.toolbar.insert(self.refresh_toolbutton,-1)
        
        self.pack_start(self.toolbar,False,False,0)

        # View
        self.scrolled_window=Gtk.ScrolledWindow()
        viewport=Gtk.Viewport()
        self.vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.textview=Gtk.TextView()
        self.textview.set_buffer(self.__create_textbuffer(dbcon))
        self.textview.set_editable(False)
        self.vbox.pack_start(self.textview,False,False,3)

        # Growlog Strains
        self.strain_view=Gtk.TreeView()
        self.strain_view.set_model(self.__create_strainview_model(dbcon))
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Breeder"),renderer,text=2)
        self.strain_view.append_column(column)

        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn(_("Strain"),renderer,text=3)
        self.strain_view.append_column(column)
        self.strain_view.connect("row_activated",self.on_strain_view_row_activated)
        self.vbox.pack_start(self.strain_view,False,False,3)
        
        # Log Entries
        self.treeview=Gtk.TreeView(self.__create_model(dbcon))
        self.treeview.connect('button-press-event',self.on_treeview_button_press_event)
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("Created on",renderer,text=1)
        self.treeview.append_column(column)

        renderer=Gtk.CellRendererText()
        renderer.props.wrap_mode=Pango.WrapMode.WORD
        column=Gtk.TreeViewColumn("Log entry",renderer,text=2)
        self.treeview.append_column(column)

        self.treeview.connect('row_activated',self.on_treeview_row_activated)
        self.treeview.get_selection().connect('changed',self.on_treeview_selection_changed)
        self.vbox.pack_start(self.treeview,True,True,3)
        
        viewport.add(self.vbox)
        self.scrolled_window.add(viewport)
        self.pack_start(self.scrolled_window,True,True,0)

        self.treeview_popup=self.__create_treeview_popup()
        self.show_all()

    def __create_treeview_popup(self):
        menu=Gtk.Menu()
        self.menuitem_new_growlog_entry=Gtk.MenuItem(label=_("New Growlog-entry"))
        menu.append(self.menuitem_new_growlog_entry)
        self.menuitem_new_growlog_entry.connect('activate', self.on_new_growlog_entry)
                
        self.menuitem_edit_growlog_entry=Gtk.MenuItem(label=_("Edit Growlog-entry"))
        menu.append(self.menuitem_edit_growlog_entry)
        self.menuitem_edit_growlog_entry.connect('activate', self.on_edit_growlog_entry)
                
        self.menuitem_delete_growlog_entry=Gtk.MenuItem(label=_("Delete Growlog-entry"))
        menu.append(self.menuitem_delete_growlog_entry)
        self.menuitem_delete_growlog_entry.connect('activate', self.on_delete_growlog_entry)

        menu.show_all()
        return menu
        
    def __create_strainview_model(self,dbcon):
        model=Gtk.ListStore(int,int,str,str)
        cursor=dbcon.execute("SELECT id,strain FROM growlog_strain WHERE growlog=?;",
                             (self.id,))
        for row in cursor:
            cursor2=dbcon.execute("SELECT breeder_name,name FROM strain_view WHERE id=?;",
                                  (row[1],))
            row2=cursor2.fetchone()
            if row2:
                model.append((row[0],row[1],row2[0],row2[1]))
        return model
        
    def __create_textbuffer(self,dbcon):
        buffer=Gtk.TextBuffer.new()
                                     
        tagtable=buffer.get_tag_table()
        tag=Gtk.TextTag.new('H1')
        tag.props.scale=3.0
        tag.props.weight=Pango.Weight.BOLD
        tagtable.add(tag)

        cursor=dbcon.execute("SELECT id,title,created_on,flower_on,finished_on,description FROM growlog WHERE id=?;", 
                             (self.id,))
        row=cursor.fetchone()
        buffer.insert_with_tags(buffer.get_start_iter(),
                                "{0}\n".format(row[1]),
                                tag)
        tag=Gtk.TextTag.new('H3')
        tag.props.weight=Pango.Weight.BOLD
        tagtable.add(tag)
        buffer.insert_with_tags(buffer.get_end_iter(), _("ID: "),tag)
        buffer.insert(buffer.get_end_iter(), "{0}\n".format(self.id))
        
        buffer.insert_with_tags(buffer.get_end_iter(),_("Created on: "),tag)
        buffer.insert(buffer.get_end_iter(),"{0}\n".format(row[2]))

        buffer.insert_with_tags(buffer.get_end_iter(),_("Flower on: "),tag)
        buffer.insert(buffer.get_end_iter(), "{0}\n".format(row[3]))

        if row[4]:
            buffer.insert_with_tags(buffer.get_end_iter(),_("Finished on: "),tag)
            buffer.insert(buffer.get_end_iter(),"{0}\n".format(row[4]))

        cdate_str,ctime_str=row[2].split(' ')
        cdate=datetime.date(*tuple((int(i) for i in cdate_str.split('-'))))
        if row[4]:
            fdate_str,ftime_str=row[4].split(' ')
            date=datetime.date(*tuple((int(i) for i in fdate_str.split('-'))))
        else:
            date=datetime.date.today()
        delta=date-cdate
        buffer.insert_with_tags(buffer.get_end_iter(),_("Age: "),tag)
        buffer.insert(buffer.get_end_iter(), _("{0} days\n").format(delta.days))

        if row[3]:
            flowering=datetime.date(*tuple((int(i) for i in row[3].split('-'))))
            delta=date-flowering
            buffer.insert_with_tags(buffer.get_end_iter(), _("Flowering: "),tag)
            buffer.insert(buffer.get_end_iter(),_("{0} days\n").format(delta.days))
            
        tag=Gtk.TextTag.new('H2')
        tag.props.scale=2.0
        tag.props.weight=Pango.Weight.BOLD
        tagtable.add(tag)

        buffer.insert_with_tags(buffer.get_end_iter(),"Description\n",tag)
        buffer.insert(buffer.get_end_iter(),row[5])

        return buffer

    def __create_model(self,dbcon):
        model=Gtk.ListStore(int,str,str)        
        cursor=dbcon.execute("SELECT id,created_on,entry FROM growlog_entry WHERE growlog=? ORDER BY created_on;",
                             (self.id,))
        cdate=datetime.date(self.created_on.year,
                            self.created_on.month,
                            self.created_on.day)
            
        for row in cursor:
            datestr,timestr=row[1].split(' ')
            y,m,d=(int(i) for i in datestr.split('-'))
            xdate=datetime.date(y,m,d)
            age=xdate-cdate

            if self.flower_on and xdate>=self.flower_on:
                flowering=xdate-self.flower_on
                txt="{0}\nAge: {1}\nFlowering: {2}".format(row[1],
                                                          age.days,
                                                          flowering.days)
            else:
                txt="{0}\nAge: {1}".format(row[1],age.days)
                
            model.append((row[0],txt,row[2]))

        return model

    def refresh(self,dbcon):
        cursor=dbcon.execute("SELECT title,flower_on,finished_on FROM growlog WHERE id=?;",(self.id,))
        row=cursor.fetchone()
        self.title_label.set_text(row[0])
        self.title_label.show()
        if row[1]:
            self.flower_toolbutton.set_sensitive(False)
            self.flower_on=datetime.date(*tuple((int(i) for i in row[1].split('-'))))

        if row[2]:
            self.finished=True
            self.finish_toolbutton.set_sensitive(False)
            datestr,timestr=row[2].split(' ')
            year,month,day=datestr.split('-')
            hour,minute,second=timestr.split(':')
            self.finished_on=datetime.datetime(year,month,day,hour,minute,second)
            self.new_log_entry_toolbutton.set_sensitive(False)
            
        self.edit_log_entry_toolbutton.set_sensitive(False)
        self.remove_log_entry_toolbutton.set_sensitive(False)
        
        self.textview.set_buffer(self.__create_textbuffer(dbcon))
        self.strain_view.set_model(self.__create_strainview_model(dbcon))
        self.treeview.set_model(self.__create_model(dbcon))
        self.show()

    def on_refresh_clicked(self,toolbutton):
        self.refresh(self.get_toplevel().dbcon)
        
    def on_treeview_selection_changed(self,selection):
        if not self.finished:
            model,iter=selection.get_selected()
            if model and iter:
                self.edit_log_entry_toolbutton.set_sensitive(True)
                self.remove_log_entry_toolbutton.set_sensitive(True)
        
    def on_edit_growlog_clicked(self,toolbutton):
        window=self.get_toplevel()
        dialog=EditGrowlogDialog(window,window.dbcon,self.id)
        result=dialog.run()
        if result == Gtk.ResponseType.APPLY:
            self.refresh(window.dbcon)
        dialog.hide()
        dialog.destroy()

    def on_flower_clicked(self,toolbutton):
        window=self.get_toplevel()
        date=datetime.date.today()
        dialog=Gtk.MessageDialog(window,
                                 flags=Gtk.DialogFlags.MODAL,
                                 message_type=Gtk.MessageType.INFO,
                                 buttons=Gtk.ButtonsType.YES_NO,
                                 message_format=_("Do you want to set flowering date to '{0}'?").format(date.isoformat()))
        result=dialog.run()
        if result==Gtk.ResponseType.YES:
            window.dbcon.execute("UPDATE growlog SET flower_on=? WHERE id=?;",
                                 (date.isoformat(),self.id))
            window.dbcon.commit()
            self.refresh(window.dbcon)
        dialog.hide()
        dialog.destroy()

    def on_finish_clicked(self,toolbutton):
        window=self.get_toplevel()
        dialog=Gtk.MessageDialog(parent=window,
                                 flags=Gtk.DialogFlags.MODAL,
                                 message_type=Gtk.MessageType.INFO,
                                 buttons=Gtk.ButtonsType.YES_NO,
                                 message_format=_("Do you really want to finish that Growlog? You will no longer be able to add,remove or edit Growlog-entries!"))
        result=dialog.run()
        if result==Gtk.ResponseType.YES:
            now=datetime.datetime.now()
            now_str=now.strftime("%Y-%m-%d %H:%M:%S")
            window.dbcon.execute("UPDATE growlog SET finished_on=? WHERE id=?;",
                                 (now_str,self.id))
            window.dbcon.commit()
            self.refresh(window.dbcon)
        dialog.hide()
        dialog.destroy()
        
    def on_edit_log_entry_clicked(self,toolbutton):
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter:
            row=model[iter]
            window=self.get_toplevel()
            dialog=GrowlogEntryDialog(window,window.dbcon,row[0])
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                self.refresh(window.dbcon)
            dialog.hide()

            dialog.destroy()

    def on_new_log_entry_clicked(self,toolbutton):
        window=self.get_toplevel()
        dialog=GrowlogEntryDialog(window,window.dbcon,growlog_id=self.id)
        result=dialog.run()
        if result==Gtk.ResponseType.APPLY:
            self.refresh(window.dbcon)
        dialog.hide()
        dialog.destroy()
            
    def on_remove_log_entry_clicked(self,toolbutton):
        window=self.get_toplevel()
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter:
            row=model[iter]
            dialog=Gtk.MessageDialog(parent=window,
                                     flags=Gtk.DialogFlags.MODAL,
                                     buttons=Gtk.ButtonsType.YES_NO,
                                     message_type=Gtk.MessageType.INFO,
                                     message_format=_("Do you really want to delete the selected growlog entry?"))
            result=dialog.run()
            if result==Gtk.ResponseType.YES:
                window.dbcon.execute("DELETE FROM growlog_entry WHERE id=?;",
                                     (row[0],))
                window.dbcon.commit()
                self.refresh(window.dbcon)
            dialog.hide()
            dialog.destroy()
        
    def on_strain_view_row_activated(self,tv,path,column):
        window=self.get_toplevel()
        model=tv.get_model()
        iter=model.get_iter(path)
        if model[iter][1]:
            page=strain.StrainView(window.dbcon,model[iter][1])
            window.add_browser_page(page)
            page.refresh(window.dbcon)
            window.show_all()

    def on_treeview_row_activated(self,tv,path,column):
        if not self.finished:
            window=self.get_toplevel()
            model=tv.get_model()
            iter=model.get_iter(path)
            dialog=GrowlogEntryDialog(window,window.dbcon,model[iter][0])
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                self.refresh(window.dbcon)
            dialog.hide()
            dialog.destroy()
        
    def on_treeview_button_press_event(self,treeview,event):
        if not self.finished:
            if (event.button == 3 
                and event.type==Gdk.EventType.BUTTON_PRESS
                and not self.finished):
                #show context menu
                self.treeview_popup.popup(None,None,None,None,event.button,event.time)

    def on_new_growlog_entry(self,widget):
        if not self.finished:
            window=growbook.application.window
            dialog=GrowlogEntryDialog(window,window.dbcon,growlog_id=self.id)
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                self.refresh(window.dbcon)
            dialog.hide()
            dialog.destroy()

    def on_edit_growlog_entry(self,widget):
        if not self.finished:
            window=self.get_toplevel()
            model,iter=self.treeview.get_selection().get_selected()
            if model and iter:
                dialog=GrowlogEntryDialog(window,window.dbcon,model[iter][0])
                result=dialog.run()
                if result==Gtk.ResponseType.APPLY:
                    self.refresh(window.dbcon)
                dialog.hide()
                dialog.destroy()

    def on_delete_growlog_entry(self,widget):
        if not self.finished:
            window=self.get_toplevel()
            model,iter=self.treeview.get_selection().get_selected()
            if model and iter:
                dialog=Gtk.MessageDialog(parent=window,
                                         flags=Gtk.DialogFlags.MODAL,
                                         message_type=Gtk.MessageType.WARNING,
                                         buttons=Gtk.ButtonsType.YES_NO,
                                         message_format=_("Do you want to delete this Growlogentry?"))
                result=dialog.run()
                if result==Gtk.ResponseType.YES:
                    try:
                        window.dbcon.execute("DELETE FROM growlog_entry WHERE id=?;",
                                             (model[iter][0],))
                        window.dbcon.commit()
                        self.refresh(window.dbcon)
                    except Exception as ex:
                        dialog2=Gtk.MessageDialog(self.get_toplevel(),
                                                  flags=Gtk.DialogFlags.MODAL,
                                                  message_type=Gtk.MessageType.ERROR,
                                                  buttons=Gtk.ButtonsType.OK,
                                                  message_format=str(ex))
                                              
                        dialog2.run()
                        dialog2.hide()
                        dialog2.destroy()
                    
                dialog.hide()
                dialog.destroy()

    def on_flowering_date_clicked(self,toolbutton):
        dialog=tools.FloweringDateDialog(self.get_toplevel(),self.flower_on)
        result=dialog.run()
        if result==Gtk.ResponseType.OK:
            pass
        dialog.hide()
        dialog.destroy()

    def on_growlog_calendar_clicked(self,toolbutton):
        window=self.get_toplevel()
        dialog=GrowlogCalendarDialog(window,window.dbcon,self.id)
        dialog.run()
        dialog.hide()
        dialog.destroy()
        
class GrowlogSelector(Gtk.ScrolledWindow):
    def __init__(self,dbcon):
        Gtk.ScrolledWindow.__init__(self)
        
        self.treeview=Gtk.TreeView(self.__init_model(dbcon))
        renderer=Gtk.CellRendererText()
        column=Gtk.TreeViewColumn("Title",renderer,text=1)
        self.treeview.append_column(column)
        self.treeview.connect('row_activated',self.on_row_activated)
        self.treeview.connect('button-press-event',self.on_treeview_button_press_event)
        self.add(self.treeview)

        self.popup=self.__create_popup(dbcon)
        
        self.show()

    def __init_model(self,dbcon):
        model=Gtk.TreeStore(int,str)

        cursor=dbcon.cursor()
        iter=model.append(None,[0,'ongoing Grows'])
        cursor.execute("SELECT id,title FROM growlog WHERE finished_on='';")
        for row in cursor:
            model.append(iter,[int(row[0]),row[1]])

        iter=model.append(None,[0,"finished Grows"])
        cursor.execute("SELECT id,title FROM growlog WHERE finished_on != '';")
        for row in cursor:
            model.append(iter,[int(row[0]),row[1]])

        iter=model.append(None,[0,'Strains'])
        cursor.execute("SELECT id,name FROM breeder ORDER BY name;")
        for breeder in cursor:
            iter2=None
            cursor2=dbcon.execute("SELECT id,name FROM strain WHERE breeder=? ORDER BY name;", (breeder[0],))
            for strain in cursor2:
                iter3=None
                cursor3=dbcon.execute("SELECT growlog,strain FROM growlog_strain WHERE strain=?;", (strain[0],))
                for logstrain in cursor3:
                    if not iter2:
                        iter2=model.append(iter,(0,breeder[1]))
                    if not iter3:
                        iter3=model.append(iter2,(0,strain[1]))
                    cursor4=dbcon.execute("SELECT id,title FROM growlog WHERE id=?;", (logstrain[0],))
                    row=cursor4.fetchone()
                    iter4=model.append(iter3,(row[0],row[1]))

        return model

    def __create_popup(self,dbcon):
        menu=Gtk.Menu()
        menuitem=Gtk.MenuItem(label=_("Open"))
        menuitem.connect('activate',lambda w:self.open_selected_growlog(dbcon))
        menu.append(menuitem)

        menuitem=Gtk.MenuItem(label=_("Edit"))
        menuitem.connect('activate', lambda w: self.edit_selected_growlog(dbcon))
        menu.append(menuitem)

        menuitem=Gtk.MenuItem(label=_("Delete"))
        menuitem.connect('activate', lambda w: self.delete_selected_growlog(dbcon))
        menu.append(menuitem)
        
        menu.show_all()
        return menu
        
    def refresh(self,dbcon):
        self.treeview.set_model(self.__init_model(dbcon))
        self.show()
        
    def on_row_activated(self,treeview,path,column):
        window=self.get_toplevel()
        model=self.treeview.get_model()
        iter=model.get_iter(path)
        row=model[iter]

        if row[0]:
            page=GrowlogView(window.dbcon,row[0])
            #window.browser.append_page(page,page.title_label)
            window.add_browser_page(page)
            window.show_all()

    def on_treeview_button_press_event(self,treeview,event):
        if event.button == 3 and event.type==Gdk.EventType.BUTTON_PRESS:
            model,iter=self.treeview.get_selection().get_selected()
            if model and iter and model[iter][0]:
                #show context menu
                self.popup.popup(None,None,None,None,event.button,event.time)

    def open_ongoing_growlogs(self,dbcon):
        window=self.get_toplevel()
        model=self.treeview.get_model()
        iter=model.get_iter_first()
        if model.iter_has_child(iter):
            n=model.iter_n_children(iter)
            for i in range(n):
                child_iter=model.iter_nth_child(iter,i)
                row=model[child_iter]
                if row[0]:
                    page=GrowlogView(dbcon,row[0])
                    window.add_browser_page(page)
        
    def open_selected_growlog(self,dbcon):
        window=self.get_toplevel()
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter:
            row=model[iter]
            if row[0]:
                page=GrowlogView(dbcon,row[0])
                window.add_browser_page(page)
                window.show_all()

    def edit_selected_growlog(self,dbcon):
        window=self.get_toplevel()
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter and model[iter][0]:
            dialog=EditGrowlogDialog(window,window.dbcon,model[iter][0])
            result=dialog.run()
            if result==Gtk.ResponseType.APPLY:
                self.refresh(window.dbcon)
                page=GrowlogView(dbcon,model[iter][0])
                window.add_browser_page(page)
                window.show_all()
            dialog.hide()
            dialog.destroy()

    def delete_selected_growlog(self,dbcon):
        window=self.get_toplevel()
        model,iter=self.treeview.get_selection().get_selected()
        if model and iter and model[iter][0]:
            cursor=dbcon.execute("SELECT title FROM growlog WHERE id=?;",
                                 (model[iter][0],))
            row=cursor.fetchone()
            dialog=Gtk.MessageDialog(parent=window,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.WARNING,
                                     buttons=Gtk.ButtonsType.YES_NO)
            dialog.set_markup(_("This deletes all data of Growlog '{0}'.\nDo you want to proceed?").format(row[0]))
            if dialog.run() == Gtk.ResponseType.YES:
                try:
                    dbcon.execute("DELETE FROM growlog_entry WHERE growlog=?;",
                                  (model[iter][0],))
                    dbcon.execute("DELETE FROM growlog_strain WHERE growlog=?;",
                                  (model[iter][0],))
                    dbcon.execute("DELETE FROM growlog WHERE id=?;",
                                  (model[iter][0],))
                    dbcon.commit()
                except Exception as ex:
                    dialog2=Gtk.MessageDialog(self.get_toplevel(),
                                              flags=Gtk.DialogFlags.MODAL,
                                              message_type=Gtk.MessageType.ERROR,
                                              buttons=Gtk.ButtonsType.OK,
                                              message_format=str(ex))
                                              
                    dialog2.run()
                    dialog2.hide()
                    dialog2.destroy()
                    
                self.refresh(dbcon)
            dialog.hide()
            dialog.destroy()

