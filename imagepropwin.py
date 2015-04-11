#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import copy

from gi.repository import GObject, Gtk
#from gi.repository import Gdk, GdkPixbuf, GObject, Gtk, GtkSource, Pango

#from ielementblock import ElementBlockInterface
from imagemodel import ImageModel

class ImagePropWin(Gtk.Window):
    __gtype_name__ = 'ImagePropWin'

    #__gsignals__ = copy.copy(ElementBlockInterface.__gsignals__)

    __instance__ = None # Singleton

    def __init__(self, **args):
        Gtk.Window.__init__(self, **args)
        self.builder = Gtk.Builder.new_from_file("imageview.ui")
        self.builder.connect_signals(self)
        container = self.builder.get_object('win-root-container')
        container.unparent()
        container.show_all()
        self.add(container)

        self.model = None
        self._sensitive_update_all()

    # TODO: This could be factorized in a super class named "Singleton"
    @classmethod
    def get_instance(cls, **args):
        if cls.__instance__ == None:
            cls.__instance__ = cls(**args)
        return cls.__instance__

    # Gtk.Widget overrides
    def do_delete_event(self, event):
        # Here we can block 'delete' signal propagation on window manager close event
        # disable right now...
        return False # True

    def do_destroy(self):
        ImagePropWin.__instance__ = None

    # Privates methods
    def _sensitive_update_all(self):
        w = self.builder.get_object('frame_img_source')
        w.set_sensitive(self.model != None)
        w = self.builder.get_object('frame_img_resize')
        w.set_sensitive(self.model != None)
        w = self.builder.get_object('frame_layout')
        w.set_sensitive(self.model != None)

        # Fixed sensitivities
        w = self.builder.get_object('button_reset_all')
        w.set_sensitive(True)
        w = self.builder.get_object('button_close')
        w.set_sensitive(True)

        if self.model:
            pass

    # Public methods
    def get_model(self):
        return self.model

    def set_model(self, model):
        b = self.builder

        s = model.get_filename()
        if s:
            w = b.get_object('filechooserbutton_filename')
            w.set_filename(s)

        # Information fields imgsrc resolution
        w = model.get_src_width()
        self.builder.get_object('entry_imgsrc_width').set_text(str(w))
        h = model.get_src_height()
        self.builder.get_object('entry_imgsrc_height').set_text(str(h))

        # Setup spinbutton ranges
        adj = Gtk.Adjustment(0, -w, w, 1, 1, 1)
        self.builder.get_object('spinbutton_layout_img_posx').configure(adj, 0, 0)
        adj = Gtk.Adjustment(0, -h, h, 1, 1, 1)
        self.builder.get_object('spinbutton_layout_img_posy').configure(adj, 0, 0)

        # Callbacks registration
        if self.model != model:
            model.connect('move', self.on_model_move)
            self.model = model

        self._sensitive_update_all()

    # Model callbacks
    def on_model_move(self, model, x, y):
        self.builder.get_object('spinbutton_layout_img_posx').set_value(x)
        #self.builder.get_object('entry_imgsrc_width').set_text(str(x))
        self.builder.get_object('spinbutton_layout_img_posy').set_value(y)
        #self.builder.get_object('entry_imgsrc_height').set_text(str(y))

    # Image source frame callbacks
    def on_filechooserbutton_filename_file_set(self, file_chooser_button):
        filename = file_chooser_button.get_filename()
        print("file_chooser_button: 'file-set' is", filename)
        self.model.load_from_file(filename)
        self.set_model(self.model) # to update UI constraints.

    # Layout callbacks
    def on_spinbutton_layout_img_posx_value_changed(self, spin_button):
        val = int(spin_button.get_value())
        x, y = self.model.get_image_coord()
        self.model.set_image_coord(val, y)
        pass

    # Window bottom buttons
    def on_button_close_clicked(self, btn):
        self.hide()

    def on_button_reset_all_clicked(self, btn):
        print("reset all parameters")

GObject.type_register(ImagePropWin)

