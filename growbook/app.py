# -*- coding: utf-8 -*-
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
import growbook
from . import config
from . import growlog
from . import strain
from . import about
from . import i18n
from . import preferences
from . import tools


_=i18n.gettext

class AppWindow(Gtk.ApplicationWindow):
    def __init__(self,dbcon,*args,**kwargs):
        self.__dbcon=dbcon
        Gtk.ApplicationWindow.__init__(self,*args,**kwargs)
        self.set_default_size(800,600)
        
        self.__vbox=Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(self.__vbox)

        # init Menubar
        ## menu/file
        self.__menubar=Gtk.MenuBar()
        menu_file=self._add_submenu(self.menubar,'File')
        submenu=menu_file.get_submenu()
        menuitem_new_growlog=self._add_menuitem(submenu,_('New Growlog'))
        menuitem_new_growlog.connect('activate',self.on_new_growlog)
        menuitem_new_breeder=self._add_menuitem(submenu,_('New Breeder'))
        menuitem_new_breeder.connect('activate',self.on_new_breeder)
        
        separator=Gtk.SeparatorMenuItem()
        menu_file.get_submenu().append(separator)
        menuitem_vacuum=self._add_menuitem(submenu,_('Vacuum'))
        menuitem_vacuum.connect('activate',self.on_vacuum)

        separator=Gtk.SeparatorMenuItem()
        menu_file.get_submenu().append(separator)
        menuitem_close=self._add_menuitem(submenu,_('Close'))
        menuitem_close.connect('activate',self.on_close)

        separator=Gtk.SeparatorMenuItem()
        menu_file.get_submenu().append(separator)
        menuitem_quit=self._add_menuitem(submenu,_('Quit'))
        menuitem_quit.connect('activate',self.on_quit)

        ## menu/edit
        menu_edit=self._add_submenu(self.menubar,_('Edit'))
        submenu=menu_edit.get_submenu()
        menuitem_preferences=self._add_menuitem(submenu,_('Preferences'))
        menuitem_preferences.connect('activate',self.on_prefereneces)

        ## menu/tools
        menu_tools=self._add_submenu(self.menubar,_('Tools'))
        submenu=menu_tools.get_submenu()
        menuitem_ventilation_calculator=self._add_menuitem(submenu,_('Ventilation Calculator'))
        menuitem_ventilation_calculator.connect('activate',self.on_ventilation_calculator)
        menuitem_power_consumtion_calulator=self._add_menuitem(submenu,_("Power Consumption Calulator"))
        menuitem_power_consumtion_calulator.connect('activate',self.on_power_consumption_calculator)
        ## menu/help
        menu_help=self._add_submenu(self.menubar,_('Help'))
        submenu=menu_help.get_submenu()
        menuitem_about=self._add_menuitem(submenu,_('About'))
        menuitem_about.connect('activate',self.on_about)
        
        self.vbox.pack_start(self.menubar,False,False,0)
        
        # init Toolbar
        self.__toolbar=Gtk.Toolbar()
        toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        toolbutton.set_tooltip_text(_('New Growlog'))
        toolbutton.connect('clicked',self.on_new_growlog)
        self.toolbar.insert(toolbutton,-1)

        separator=Gtk.SeparatorToolItem()
        self.toolbar.insert(separator,-1)
        
        toolbutton=Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
        toolbutton.set_tooltip_text(_('New Breeder'))
        toolbutton.connect('clicked',self.on_new_breeder)
        self.toolbar.insert(toolbutton,-1)
        
        self.vbox.pack_start(self.toolbar,False,False,0)

        # init content area
        hpaned=Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

        # init selector
        self.__selector=Gtk.Notebook()
        self.selector.set_scrollable(True)

        label=Gtk.Label(_('GrowLog'))
        self.__growlog_selector=growlog.GrowlogSelector(self.dbcon)
        self.selector.append_page(self.growlog_selector,label)

        label=Gtk.Label(_('Strains'))
        self.__strain_selector=strain.StrainSelector(self.dbcon)
        self.selector.append_page(self.strain_selector,label)
        
        hpaned.add1(self.selector)

        # init browser
        self.__browser=Gtk.Notebook()
        self.browser.set_scrollable(True)
        hpaned.add2(self.browser)

        self.vbox.pack_start(hpaned,True,True,0)

        self.__statusbar=Gtk.Statusbar()
        self.vbox.pack_end(self.statusbar,False,False,0)

        if config.config['open-ongoing-growlogs']:
            self.growlog_selector.open_ongoing_growlogs(self.dbcon)

        self.show_all()

    @property
    def dbcon(self):
        return self.__dbcon

    @property
    def vbox(self):
        return self.__vbox

    @property
    def menubar(self):
        return self.__menubar

    @property
    def toolbar(self):
        return self.__toolbar
        
    @property
    def selector(self):
        return self.__selector

    @property
    def growlog_selector(self):
        return self.__growlog_selector

    @property
    def strain_selector(self):
        return self.__strain_selector
        
    @property
    def browser(self):
        return self.__browser

    @property
    def statusbar(self):
        return self.__statusbar

    def _add_submenu(self,menubar,label):
        menuitem=Gtk.MenuItem(label=label)
        menubar.append(menuitem)
        submenu=Gtk.Menu()
        menuitem.set_submenu(submenu)
        return menuitem

    def _add_menuitem(self,submenu,label):
        menuitem=Gtk.MenuItem(label=label)
        submenu.append(menuitem)
        return menuitem

    def add_browser_page(self,widget):
        for pageno in xrange(self.browser.get_n_pages()):
            page=self.browser.get_nth_page(pageno)
            
            if page.type==widget.type and page.id==widget.id:
                self.browser.set_current_page(pageno)
                page.refresh(self.dbcon)
                return

        def _on_title_close(button,widget):
            pageno=self.browser.page_num(widget)
            self.browser.remove_page(pageno)

        # tab with close-button
        hbox=Gtk.HBox()
        hbox.pack_start(widget.title_label,False,False,0)

        close_image=Gtk.Image.new_from_stock(Gtk.STOCK_CLOSE,Gtk.IconSize.MENU)
        button=Gtk.Button()
        button.set_relief(Gtk.ReliefStyle.NONE)
        button.set_focus_on_click(False)
        button.add(close_image)
        button.connect('clicked',_on_title_close,widget)
        hbox.pack_start(button,False,False,0)

        hbox.show_all()
        widget.show()
        self.browser.append_page(widget,hbox)
        self.browser.set_current_page(-1)
        self.browser.show()
        
    def on_new_breeder(self,widget):
        dialog=strain.NewBreederDialog(self, self.dbcon)
        dialog.show_all()
        result=dialog.run()
        if result==Gtk.ResponseType.APPLY:
            #recreate table
            self.strain_selector.refresh(self.dbcon)
            cursor=self.dbcon.cursor()
            cursor.execute('SELECT id FROM breeder WHERE name=?;',
                           (dialog.name_entry.get_text(),))
            row=cursor.fetchone()
            dialog.hide()
            dialog2=strain.EditBreederDialog(self,self.dbcon,row[0])
            result2=dialog2.run()
            if result2 == Gtk.ResponseType.APPLY:
                pass
                
            dialog2.hide()
            dialog2.destroy()
            dialog.destroy()
            self.strain_selector.refresh(self.dbcon)
        else:
            dialog.hide()
            dialog.destroy()

    def on_new_growlog(self,widget):
        dialog=growlog.NewGrowlogDialog(self,self.dbcon)
        result=dialog.run()
        if result==Gtk.ResponseType.APPLY:
            dialog.hide()
            cursor=self.dbcon.execute('SELECT id FROM growlog WHERE title=?',
                                      (dialog.title_entry.get_text(),))
            row=cursor.fetchone()
            if row:
                dialog2=growlog.EditGrowlogDialog(self,self.dbcon,row[0])
                result2=dialog2.run()

                if result2 == Gtk.ResponseType.APPLY:
                    pass
                dialog2.hide()
                dialog2.destroy()
            
                self.growlog_selector.refresh(self.dbcon)
                page=growlog.GrowlogView(self.dbcon,row[0])
                self.add_browser_page(page)
        else:
            dialog.hide()
        dialog.destroy()

    def on_close(self,widget):
        if self.browser.get_n_pages() > 0:
            pageno=self.browser.get_current_page()
            self.browser.remove_page(pageno)

    def on_quit(self,widget):
        self.hide()
        self.destroy()
        
    def on_vacuum(self,widget):
        try:
            self.dbcon.execute("VACUUM;")
            self.dbcon.commit()

            dialog=Gtk.MessageDialog(parent=self,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.INFO,
                                     buttons=Gtk.ButtonsType.OK,
                                     message_format=_("'VACUUM' successfully run on database!"))
        except:
            dialog=Gtk.MessageDialog(parent=self,
                                     flags=Gtk.DialogFlags.MODAL,
                                     message_type=Gtk.MessageType.ERROR,
                                     message_format=_("'VACUUM' failed!"),
                                     buttons=Gtk.ButtonsType.OK)
        dialog.run()
        dialog.hide()
        dialog.destroy()

    def on_prefereneces(self,widget):
        dialog=preferences.PreferencesDialog(self,growbook.application.dbcon)
        result=dialog.run()
        if result == Gtk.ResponseType.APPLY:
            pass
        dialog.hide()
        dialog.destroy()

    def on_ventilation_calculator(self,widget):
        page=tools.VentilationCalculator(self.dbcon)
        self.add_browser_page(page)

    def on_about(self,widget):
        dialog=about.AboutDialog(self)
        dialog.run()
        dialog.hide()
        dialog.destroy()

    def on_power_consumption_calculator(self,widget):
        page=tools.PowerConsumptionCalculator(self.dbcon)
        self.add_browser_page(page)

    def do_destroy(self):
        if self.dbcon != growbook.application.dbcon:
            self.dbcon.close()
        growbook.application._clear_window()
        growbook.application.quit()
        
class Application(Gtk.Application):
    def __init__(self,*args,**kwargs):
        Gtk.Application.__init__(self,
                                 *args,
                                 application_id='org.example.growbook',
                                 flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
                                 **kwargs)
        self.__window=None
        self.__dbcon=None

        self.add_main_option('open',
                             ord('o'),
                             GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE,
                             _("Open ongoing growlogs."),
                             None)
        self.add_main_option('not-open',
                             ord('O'),
                             GLib.OptionFlags.NONE,
                             GLib.OptionArg.NONE,
                             _("Don't open ongoing growlogs."),
                             None)
                             
                             
    @property
    def window(self):
        return self.__window

    def _clear_window(self):
        self.__window=None
        
    @property
    def dbcon(self):
        return self.__dbcon
        
    def do_startup(self):
        Gtk.Application.do_startup(self)

        #init datadir
        if not os.path.exists(config.config['datadir']):
            os.makedirs(config.config['datadir'])

        #init database
        if not os.path.exists(config.config['dbfile']):
            self.__dbcon=sqlite3.connect(config.config['dbfile'])
            with open(config.config['sql-file'],'r') as f:
                self.dbcon.executescript(f.read())
        else:
            self.__dbcon=sqlite3.connect(config.config['dbfile'])
        self.dbcon.text_factory=str

        #init config
        config.init_config(self.dbcon)

    def do_activate(self):
        Gtk.Application.do_activate(self)
        if not self.window:
            self.__window=AppWindow(self.dbcon,application=self,title=_("GrowBook"))
        self.window.present()

    def do_command_line(self,command_line):
        Gtk.Application.do_command_line(self,command_line)

        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if 'open' in options:
            config.config['open-ongoing-growlogs'] = True
        if 'not-open' in options:
            config.config['open-ongoing-growlogs'] = False
        
        self.activate()
        
        return 0

    def do_shutdown(self):
        self.dbcon.close()
        Gtk.Application.do_shutdown(self)

