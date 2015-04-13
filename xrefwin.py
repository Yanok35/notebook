#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import binascii
import copy

from gi.repository import Gdk, GObject, Gtk
#from gi.repository import Gdk, GdkPixbuf, GObject, Gtk, GtkSource, Pango

#from ielementblock import ElementBlockInterface

class XRefWin(Gtk.Window):
    __gtype_name__ = 'XRefWin'

    #__gsignals__ = copy.copy(ElementBlockInterface.__gsignals__)

    __instance__ = None # Singleton

    def __init__(self, **args):
        Gtk.Window.__init__(self, **args)
        self.builder = Gtk.Builder.new_from_file("xref.ui")
        self.builder.connect_signals(self)
        container = self.builder.get_object('win-root-container')
        container.unparent()
        container.show_all()
        self.add(container)
        self.set_size_request(300, 400)

        self.treeview = self.builder.get_object('treeview_subdocs')
        self.treeview.expand_all()

        column_title = ['Document name' ] #, 'DocID']
        for i in range(0, len(column_title)):
            renderer = Gtk.CellRendererText()
            #if i == 0:
            #    renderer.connect("edited", self.on_treeview_cell_edited)
            #    renderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title[i], renderer, text=i)
            self.treeview.append_column(column)

        self.treeview.show_all()

        # Set the label preview to have a white background
        label_preview = self.builder.get_object('label_preview')
        label_preview.override_background_color(Gtk.StateFlags.NORMAL,
                                                Gdk.RGBA(1, 1, 1, 1))

        label_preview.drag_source_set(Gdk.ModifierType.BUTTON1_MASK, [], Gdk.DragAction.COPY)
        #label_preview.drag_source_add_text_targets()

        targets = Gtk.TargetList.new([])
        #targets.add_text_targets(0) # common for major apps...
        targets.add_text_targets(1) # prioprietary format with a serialized string.
        #targets.add_uri_targets(1)
        label_preview.drag_source_set_target_list(targets)

        #label_preview.connect('drag-begin', self.on_label_preview_drag_begin)
        label_preview.connect('drag-data-get', self.on_label_preview_drag_data_get)

        self.textmodel = None
        self._sensitive_update_all()

        self.xref = u''

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
        #w = self.builder.get_object('frame_img_source')
        #w.set_sensitive(self.model != None)
        #w = self.builder.get_object('frame_img_resize')
        #w.set_sensitive(self.model != None)
        #w = self.builder.get_object('frame_layout')
        #w.set_sensitive(self.model != None)

        # Fixed sensitivities
        #w = self.builder.get_object('button_reset_all')
        #w.set_sensitive(True)
        w = self.builder.get_object('button_close')
        w.set_sensitive(True)

        #if self.model:
        #    pass

    # Public methods

    def set_treemodel(self, model):
        #b = self.builder
        self.treeview.set_model(model)
        self.treeview.expand_all()

        #s = model.get_filename()
        #if s:
        #    w = b.get_object('filechooserbutton_filename')
        #    w.set_filename(s)

        ## Information fields imgsrc resolution
        #w = model.get_src_width()
        #self.builder.get_object('entry_imgsrc_width').set_text(str(w))
        #h = model.get_src_height()
        #self.builder.get_object('entry_imgsrc_height').set_text(str(h))

        ## Setup spinbutton ranges
        #adj = Gtk.Adjustment(0, -w, w, 1, 1, 1)
        #self.builder.get_object('spinbutton_layout_img_posx').configure(adj, 0, 0)
        #adj = Gtk.Adjustment(0, -h, h, 1, 1, 1)
        #self.builder.get_object('spinbutton_layout_img_posy').configure(adj, 0, 0)

        ## Callbacks registration
        #if self.model != model:
        #    model.connect('move', self.on_model_move)
        #    self.model = model

        self._sensitive_update_all()

    def set_textmodel(self, model):
        self.textmodel = model

    ## Model callbacks
    #def on_model_move(self, model, x, y):
    #    self.builder.get_object('spinbutton_layout_img_posx').set_value(x)
    #    #self.builder.get_object('entry_imgsrc_width').set_text(str(x))
    #    self.builder.get_object('spinbutton_layout_img_posy').set_value(y)
    #    #self.builder.get_object('entry_imgsrc_height').set_text(str(y))

    ## Image source frame callbacks
    #def on_filechooserbutton_filename_file_set(self, file_chooser_button):
    #    filename = file_chooser_button.get_filename()
    #    print("file_chooser_button: 'file-set' is", filename)
    #    self.model.load_from_file(filename)
    #    self.set_model(self.model) # to update UI constraints.

    ## Layout callbacks
    #def on_spinbutton_layout_img_posx_value_changed(self, spin_button):
    #    val = int(spin_button.get_value())
    #    x, y = self.model.get_image_coord()
    #    self.model.set_image_coord(val, y)
    #    pass

    # External links widgets
    def on_entry_link_url_changed(self, entry):
        #print entry.get_text()
        link_url = entry.get_text()
        entry_link_text = self.builder.get_object('entry_link_text')
        link_text = entry_link_text.get_text()

        if link_text == "" or link_url.startswith(link_text) or link_text.startswith(link_url):
            entry_link_text.set_text(link_url)
        entry_link_text.emit('changed')

    def on_entry_link_text_changed(self, entry):
        #print entry.get_text()
        entry_link_url = self.builder.get_object('entry_link_url')
        label_preview = self.builder.get_object('label_preview')

        # 'push' external link data to preview ...
        label_preview.set_markup("<a href='" + entry_link_url.get_text() + "'>" + entry.get_text() + "</a>")

        # ... and to self.xref
        tag = self.textmodel.create_url_tag(entry.get_text(),
                                            entry_link_url.get_text())
        self.xref = tag.tostring()

    # Preview 'label' callbacks

    #def on_label_preview_drag_begin(self, widget, context):
    #    print("on_label_preview_drag_begin")
    #    pass

    def on_label_preview_drag_data_get(self, widget, context, data, info, time):
        #print("on_label_preview_drag_data_get", info)
        label_preview = self.builder.get_object('label_preview')
        if info == 0: # default for all apps
            data.set_text(label_preview.get_label(), -1)
        elif info == 1: # serialized data in a hexified string
            data.set_text(self.xref, -1)

    # Window bottom buttons
    def on_button_close_clicked(self, btn):
        self.hide()

    #def on_button_reset_all_clicked(self, btn):
    #    print("reset all parameters")

GObject.type_register(XRefWin)

