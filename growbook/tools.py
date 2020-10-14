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

import i18n
_=i18n.gettext


class VentilationCalculator(Gtk.Grid):
    (type,)=("VentilationCalculator",)
    def __init__(self,dbcon):
        self.id=0
        self.title_label=Gtk.Label(_("Ventilation"))
        Gtk.Grid.__init__(self)

        label=Gtk.Label(_("Width [m]:"))
        self.attach(label,0,0,1,1)
        adjustment=Gtk.Adjustment.new(1.0,0.1,100.0,0.1,1.0,10.0)
        self.width_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.width_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.width_spinbutton,1,0,1,1)

        label=Gtk.Label(_("Depth [m]:"))
        self.attach(label,0,1,1,1)
        adjustment=Gtk.Adjustment.new(1.0,0.1,100.0,0.1,1.0,10.0)
        self.depth_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.depth_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.depth_spinbutton,1,1,1,1)

        label=Gtk.Label(_("Height [m]:"))
        self.attach(label,0,2,1,1)
        adjustment=Gtk.Adjustment.new(2.0,0.1,100.0,0.1,1.0,10.0)
        self.height_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.height_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.height_spinbutton,1,2,1,1)

        label=Gtk.Label(_("Tube length [m]:"))
        self.attach(label,0,3,1,1)
        adjustment=Gtk.Adjustment.new(1.0,0.1,100.0,0.1,1.0,10.0)
        self.tubelength_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.tubelength_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.tubelength_spinbutton,1,3,1,1)

        label=Gtk.Label(_("Buffer:"))
        self.attach(label,0,4,1,1)
        adjustment=Gtk.Adjustment.new(2.0,0.1,100.0,0.1,1.0,10.0)
        self.buffer_spinbutton=Gtk.SpinButton.new(adjustment,0.1,1)
        self.buffer_spinbutton.connect('value-changed',self.on_spinbutton_value_changed)
        self.attach(self.buffer_spinbutton,1,4,1,1)

        #self.calc_button=Gtk.Button.new_with_label(_("Calculate"))
        #self.calc_button.connect('clicked',self.on_calculate_clicked)
        #self.attach(self.calc_button,1,5,1,1)

        label=Gtk.Label(_("Recommended capacity:"))
        self.attach(label,0,5,1,1)
        self.result_label=Gtk.Label()
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

        self.result_label.set_text("{0} m3/h".format(str(value)))
        self.result_label.show()

        
