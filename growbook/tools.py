# -*- coding: utf-8 -*-
# growbook/tools.py
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
from gi.repository import Gtk
import datetime
import i18n
_=i18n.gettext
from collections import namedtuple

class VentilationCalculator(Gtk.Grid):
    (type,)=("VentilationCalculator",)
    def __init__(self,dbcon):
        self.id=0
        self.title_label=Gtk.Label(_("Ventilation"))
        Gtk.Grid.__init__(self)

        label=Gtk.Label(_("Width [m]:"))
        label.set_xalign(0.0)
        self.attach(label,0,0,1,1)
        adjustment=Gtk.Adjustment.new(1.0,0.1,100.0,0.1,1.0,10.0)
        self.width_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.width_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.width_spinbutton,1,0,1,1)

        label=Gtk.Label(_("Depth [m]:"))
        label.set_xalign(0.0)
        self.attach(label,0,1,1,1)
        adjustment=Gtk.Adjustment.new(1.0,0.1,100.0,0.1,1.0,10.0)
        self.depth_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.depth_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.depth_spinbutton,1,1,1,1)

        label=Gtk.Label(_("Height [m]:"))
        label.set_xalign(0.0)
        self.attach(label,0,2,1,1)
        adjustment=Gtk.Adjustment.new(2.0,0.1,100.0,0.1,1.0,10.0)
        self.height_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.height_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.height_spinbutton,1,2,1,1)

        label=Gtk.Label(_("Tube length [m]:"))
        label.set_xalign(0.0)
        self.attach(label,0,3,1,1)
        adjustment=Gtk.Adjustment.new(1.0,0.1,100.0,0.1,1.0,10.0)
        self.tubelength_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.tubelength_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.tubelength_spinbutton,1,3,1,1)

        label=Gtk.Label(_("Buffer:"))
        label.set_xalign(0.0)
        self.attach(label,0,4,1,1)
        adjustment=Gtk.Adjustment.new(2.0,0.1,100.0,0.1,1.0,10.0)
        self.buffer_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.buffer_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.buffer_spinbutton,1,4,1,1)

        label=Gtk.Label(_("Recommended capacity:"))
        label.set_xalign(0.0)
        self.attach(label,0,5,1,1)
        self.result_label=Gtk.Label()
        self.result_label.set_xalign(0.5)
        self.attach(self.result_label,1,5,1,1)

        self.calculate()
        self.show_all()

    def on_spinbutton_value_changed(self,spinbutton):
        self.calculate()
        
    def calculate(self):
        width=self.width_spinbutton.get_value()
        height=self.height_spinbutton.get_value()
        depth=self.depth_spinbutton.get_value()
        tubelength=self.tubelength_spinbutton.get_value()
        buffer=self.buffer_spinbutton.get_value()

        value=(width*height*depth*1.35 + tubelength)*60/3*buffer

        self.result_label.set_text("{0} m³/h".format(str(value)))
        self.result_label.show()


class FloweringDateDialog(Gtk.Dialog):
    def __init__(self,parent,flowering_start=None):
        Gtk.Dialog.__init__(self,
                            title=_("Flowering Time"),
                            parent=parent)
        self.add_button("OK",Gtk.ResponseType.OK)
        
        if flowering_start:
            self.flowering_start=flowering_start
        else:
            self.flowering_start=datetime.date.today()
            
        vbox=self.get_content_area()
        grid=Gtk.Grid()
        label=Gtk.Label(_("Start Flowering:"))
        grid.attach(label,0,0,1,1)
        self.flowering_start_label=Gtk.Label(self.flowering_start.isoformat())
        grid.attach(self.flowering_start_label,1,0,1,1)

        label=Gtk.Label(_("Flowering days:"))
        grid.attach(label,0,1,1,1)
        adjustment=Gtk.Adjustment.new(60.0,1.0,365.0,1.0,10.0,10.0)
        self.flowering_days_spinbutton=Gtk.SpinButton.new(adjustment,1.0,0)
        self.flowering_days_spinbutton.connect("value-changed",self.on_flowering_days_value_changed)
        grid.attach(self.flowering_days_spinbutton,1,1,1,1)
        
        label=Gtk.Label(_("Finished on:"))
        grid.attach(label,0,2,1,1)
        self.finish_on_label=Gtk.Label()
        grid.attach(self.finish_on_label,1,2,1,1)
        self.calculate_finish_on(self.flowering_days_spinbutton.get_value_as_int())
        
        vbox.pack_start(grid,True,True,0)
        self.show_all()
        
    def on_flowering_days_value_changed(self,spinbutton):
        self.calculate_finish_on(spinbutton.get_value_as_int())

    def calculate_finish_on(self,days):
        delta=datetime.timedelta(days)
        finish_on=self.flowering_start + delta
        self.finish_on_label.set_text(finish_on.isoformat())

class PowerConsumptionCalculator(Gtk.ScrolledWindow):
    (type,) = ("PowerConsumptionCalculator",)
    
    def __init__(self,dbcon):
        Gtk.ScrolledWindow.__init__(self)
        self.id=0
        self.title_label=Gtk.Label(_("Power Consumption"))
        viewport=Gtk.Viewport.new()
        
        grid=Gtk.Grid.new()
        label=Gtk.Label(_("Grow"))
        grid.attach(label,0,0,1,1)
        
        label=Gtk.Label(_("Ballast [W]:"))
        grid.attach(label,0,1,1,1)
        adjustment=Gtk.Adjustment.new(400.0,1.0,10000.0,10.0,50.0,1.0)
        self.grow_ballast_spinbutton=Gtk.SpinButton.new(adjustment,10,0)
        grid.attach(self.grow_ballast_spinbutton,1,1,1,1)

        label=Gtk.Label(_("Time per day [h]:"))
        grid.attach(label,2,1,1,1)
        adjustment=Gtk.Adjustment.new(18.0,1.0,24.0,1.0,6.0,1.0)
        self.grow_time_spinbutton=Gtk.SpinButton.new(adjustment,1,0)
        grid.attach(self.grow_time_spinbutton,3,1,1,1)

        label=Gtk.Label(_("Duration [days]:"))
        grid.attach(label,0,2,1,1)
        adjustment=Gtk.Adjustment(14.0,0.0,365.0,1.0,7.0,1.0)
        self.grow_days_spinbutton=Gtk.SpinButton.new(adjustment,1,0)
        grid.attach(self.grow_days_spinbutton,1,2,1,1)
        
        separator=Gtk.HSeparator()
        grid.attach(separator,0,3,4,1)
        
        label=Gtk.Label(_("Flower"))
        grid.attach(label,0,4,1,1)
        label=Gtk.Label(_("Ballast [W]:"))
        grid.attach(label,0,5,1,1)
        adjustment=Gtk.Adjustment.new(400.0,1.0,10000.0,10.0,50.0,1.0)
        self.flower_ballast_spinbutton=Gtk.SpinButton.new(adjustment,10,0)
        grid.attach(self.flower_ballast_spinbutton,1,5,1,1)

        label=Gtk.Label(_("Time per day [h]:"))
        grid.attach(label,2,5,1,1)
        adjustment=Gtk.Adjustment.new(12.0,1.0,24.0,1.0,6.0,1.0)
        self.flower_time_spinbutton=Gtk.SpinButton.new(adjustment,1,0)
        grid.attach(self.flower_time_spinbutton,3,5,1,1)

        label=Gtk.Label(_("Duration [days]:"))
        grid.attach(label,0,6,1,1)
        adjustment=Gtk.Adjustment(60.0,0.0,365.0,1.0,7.0,1.0)
        self.flower_days_spinbutton=Gtk.SpinButton.new(adjustment,1,0)
        grid.attach(self.flower_days_spinbutton,1,6,1,1)

        separator=Gtk.HSeparator()
        grid.attach(separator,0,7,4,1)

        label=Gtk.Label(_('Exhaust System [W]:'))
        grid.attach(label,0,8,1,1)
        adjustment=Gtk.Adjustment(0.0,0.0,10000.0,10.0,50.0,1.0)
        self.exhaust_system_spinbutton=Gtk.SpinButton.new(adjustment,10,0)
        grid.attach(self.exhaust_system_spinbutton,1,8,1,1)
        
        viewport.add(grid)
        self.add(viewport)
        self.show_all()

    @property
    def grow_ballast(self):
        return self.grow_ballast_spinbutton.get_value_as_int()

    @property
    def grow_time(self):
        return self.grow_time_spinbutton.get_value_as_int()

    @property
    def grow_days(self):
        return self.grow_days_spinbutton.get_value_as_int()

    @property
    def flower_ballast(self):
        return self.flower_ballast_spinbutton.get_value_as_int()

    @property
    def flower_time(self):
        return self.flower_time_spinbutton.get_value_as_int()

    @property
    def flower_days(self):
        return self.flower_days_spinbutton.get_value_as_int()

    @property
    def exhaust_system(self):
        return self.exhaust_system_spinbutton.get_value_as_int()
        
