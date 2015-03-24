#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, Gio, Gtk, Pango
from projecttreeview import ProjectTreeView
from editortextview import EditorTextView

class NotebookApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id="apps.notebook",
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.connect("activate", self.on_activate)
        #self.connect("delete-event", Gtk.main_quit)

    def on_activate(self, data=None):

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.set_title("TextView Example")
        self.window.connect("delete-event", Gtk.main_quit)
        self.add_window(self.window)

        self.window.set_default_size(-1, 350)

        self.grid = Gtk.Grid()
        self.window.add(self.grid)

        self.projecttreeview = ProjectTreeView()
        self.projecttreeview.set_property('width-request', 200)
        self.grid.attach(self.projecttreeview, 0, 0, 1, 2)
        #self.create_textview()

        self.editortextview = self.projecttreeview.get_editor_widget()
        self.grid.attach(self.editortextview, 1, 1, 2, 1)

        #assert (self.editortextview is not None)
        self.create_toolbar(None)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.window.connect('key-press-event', self.on_key_press_event)
        self.window.show_all()

    def create_toolbar(self, editortextview):
        toolbar = Gtk.Toolbar()
        self.grid.attach(toolbar, 1, 0, 2, 1)

        button_bold = Gtk.ToolButton.new_from_stock(Gtk.STOCK_BOLD)
        toolbar.insert(button_bold, 0)

        button_italic = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ITALIC)
        toolbar.insert(button_italic, 1)

        button_underline = Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDERLINE)
        toolbar.insert(button_underline, 2)

        #button_bold.connect("clicked", self.on_button_clicked,
        #    editortextview.get_tag_bold())
        #button_italic.connect("clicked", self.on_button_clicked,
        #    editortextview.get_tag_italic())
        #button_underline.connect("clicked", self.on_button_clicked,
        #    editortextview.get_tag_underline())

        toolbar.insert(Gtk.SeparatorToolItem(), 3)

        radio_justifyleft = Gtk.RadioToolButton()
        radio_justifyleft.set_stock_id(Gtk.STOCK_JUSTIFY_LEFT)
        toolbar.insert(radio_justifyleft, 4)

        radio_justifycenter = Gtk.RadioToolButton.new_with_stock_from_widget(
            radio_justifyleft, Gtk.STOCK_JUSTIFY_CENTER)
        toolbar.insert(radio_justifycenter, 5)

        radio_justifyright = Gtk.RadioToolButton.new_with_stock_from_widget(
            radio_justifyleft, Gtk.STOCK_JUSTIFY_RIGHT)
        toolbar.insert(radio_justifyright, 6)

        radio_justifyfill = Gtk.RadioToolButton.new_with_stock_from_widget(
            radio_justifyleft, Gtk.STOCK_JUSTIFY_FILL)
        toolbar.insert(radio_justifyfill, 7)

        radio_justifyleft.connect("toggled", self.on_justify_toggled,
            Gtk.Justification.LEFT)
        radio_justifycenter.connect("toggled", self.on_justify_toggled,
            Gtk.Justification.CENTER)
        radio_justifyright.connect("toggled", self.on_justify_toggled,
            Gtk.Justification.RIGHT)
        radio_justifyfill.connect("toggled", self.on_justify_toggled,
            Gtk.Justification.FILL)

        toolbar.insert(Gtk.SeparatorToolItem(), 8)

        button_clear = Gtk.ToolButton.new_from_stock(Gtk.STOCK_CLEAR)
        button_clear.connect("clicked", self.on_clear_clicked)
        toolbar.insert(button_clear, 9)

        toolbar.insert(Gtk.SeparatorToolItem(), 10)

        open_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_OPEN)
        open_btn.connect("clicked", self.on_open_clicked)
        toolbar.insert(open_btn, 11)
        save_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_SAVE)
        save_btn.connect("clicked", self.on_save_clicked)
        toolbar.insert(save_btn, 12)

#    def create_textview(self):
#        self.editortextview = EditorTextView()
#        self.grid.attach(self.editortextview, 1, 1, 2, 1)

    def on_button_clicked(self, widget, tag):
        self.editortextview.on_apply_tag(widget, tag)

    def on_clear_clicked(self, widget):
        self.editortextview.on_remove_all_tags(widget)

    def on_justify_toggled(self, widget, justification):
        self.editortextview.on_justify_toggled(widget, justification)

    def on_open_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected_file = dialog.get_filename()
            #self.editortextview.load_from_file(selected_file)
            self.projecttreeview.load_from_file(selected_file)
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        dialog.destroy()

    def on_save_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Save file", self.window,
        Gtk.FileChooserAction.SAVE,
        (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
         Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            save_file = dialog.get_filename()
            #self.editortextview.save_to_file(save_file)
            self.projecttreeview.save_to_file(save_file)
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        dialog.destroy()

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        # debug string :
        #print(key + str(event.state))

        if event.state & Gdk.ModifierType.CONTROL_MASK and key in ('o', 's', 'v'):
            if key == 'o':
                self.on_open_clicked(None)
            elif key == 's':
                self.on_save_clicked(None)
            elif key == 'v':
                pixbuf = self.clipboard.wait_for_image()
                if pixbuf != None:
                    self.editortextview.insert_pixbuf_at_cursor(pixbuf)
                else:
                    return False

            #print ('event catched')
            return True

        return False

    def set_editor_widget(self, widget):
        self.editortextview = widget
        #self.grid.attach(self.editortextview, 1, 1, 2, 1)

if __name__ == "__main__":
    app = NotebookApp()
    app.run(None)

