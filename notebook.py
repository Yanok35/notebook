#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import sys, os

from gi.repository import Gdk, Gio, Gtk, Pango

import glade_custom_catalog

APP_TITLE = "Notebook"

class NotebookApp(Gtk.Application):

    def __init__(self):
        Gtk.Application.__init__(self, application_id="apps.notebook",
                                 flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.connect("activate", self.on_activate)
        self.connect("open", self.on_open)

        self.builder = Gtk.Builder.new_from_file("notebook.ui")
        self.builder.connect_signals(self)

        self.projecttreeview = self.builder.get_object("projecttreeview1")
        self.projecttreeview.connect('subdoc-inserted', self.on_subdoc_inserted)
        self.projecttreeview.connect('subdoc-deleted', self.on_subdoc_deleted)
        self.projecttreeview.connect('subdoc-changed', self.on_subdoc_changed)
        self.projecttreeview.connect('subdoc-load-from-file', self.on_subdoc_load_from_file)
        self.projecttreeview.connect('subdoc-save-to-file', self.on_subdoc_save_to_file)
        self.projecttreeview.connect('subdoc-order-changed', self.on_subdoc_order_changed)
        self.projecttreeview.connect('subdoc-selection-changed', self.on_subdoc_selection_changed)
        self.projecttreeview.connect('project-export', self.on_project_export)

        self.projview = self.builder.get_object("projectview1")
        #self.projview.add(GtkSource.View())
        #self.projview.add(Gtk.TextView())

        self.hpaned = self.builder.get_object("paned1")
        self.hpaned.set_position(200)
        
        self.project_filename = None

    def on_activate(self, data=None):

        accel = self.builder.get_object("accelgroup1")
        self.window = self.builder.get_object("window1")
        self.window.set_title(APP_TITLE)
        self.window.add_accel_group(accel)
        self.window.show_all()

        self.add_window(self.window)

    def on_open(self, application, files, hint, data):

        for f in files:
            print("cmdline ask open: ", f.get_parse_name())
            self.projecttreeview.load_from_file(f.get_parse_name())
            self.project_filename = f.get_parse_name()
            break # todo: multiple project support
        
        self.activate()
        self.update_window_title()

    def update_window_title(self):
        if self.project_filename:
            wintitle = os.path.basename(self.project_filename) + ' - ' + APP_TITLE
            self.window.set_title(wintitle)

    def update_subdoc_title(self, docid = None):
        doclist = self.projecttreeview.get_doc_list()
        for doc in doclist:
            curid = doc[0]
            curtitle = doc[1]
            if (not docid) or (docid and docid == curid):
                self.projview.subdoc_set_title(curid, curtitle)

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


    def on_subdoc_inserted(self, projecttreeview, docid):
        print('*** on_subdoc_inserted signal received, docid = ' + str(docid))
        self.projview.subdoc_new(docid)

    def on_subdoc_deleted(self, projecttreeview, docid):
        print('*** TODO: on_subdoc_deleted signal received, docid = ' + str(docid))
        #self.projview.subdoc_set_visible(None)
        pass

    def on_subdoc_changed(self, projecttreeview, docid):
        print('*** on_subdoc_changed signal received, docid = ' + str(docid))
        self.update_subdoc_title(docid)

    def on_subdoc_load_from_file(self, projecttreeview, docid, filename):
        print('*** on_subdoc_load_from_file signal received, docid = ' + str(docid))
        print('filename = ' + str(filename))
        self.projview.subdoc_load_from_file(docid, filename)
        self.update_subdoc_title(docid)

    def on_subdoc_save_to_file(self, projecttreeview, docid, filename):
        print('*** on_subdoc_save_to_file signal received, docid = ' + str(docid))
        print('filename = ' + str(filename))
        self.projview.subdoc_save_to_file(docid, filename)

    def on_subdoc_order_changed(self, projecttreeview):
        print('*** on_subdoc_order_changed signal received')
        pass

    def on_subdoc_selection_changed(self, projecttreeview):
        print('*** on_subdoc_selection_changed signal received')
        sel_list = projecttreeview.get_selection_list()
        print(len(sel_list), sel_list)
        self.projview.subdoc_set_visible(sel_list)

    def on_project_export(self, projecttreeview):
        text = ""
        docids = projecttreeview.get_docid_list()
        for docid in docids:
            text += self.projview.subdoc_get_content_as_text(docid)
        print text
        pass

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

            self.project_filename = selected_file
            self.update_window_title()
        elif response == Gtk.ResponseType.CANCEL:
            dialog.destroy()

        dialog.destroy()

    def on_save_clicked(self, widget, force_dialog = False):
        if force_dialog or self.project_filename is None:
            dialog = Gtk.FileChooserDialog("Save file", self.window,
                            Gtk.FileChooserAction.SAVE,
                            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                             Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                save_file = dialog.get_filename()
            elif response == Gtk.ResponseType.CANCEL:
                dialog.destroy()
                return
            dialog.destroy()
        else:
            save_file = self.project_filename

        self.projecttreeview.save_to_file(save_file)
        self.project_filename = save_file
        self.update_window_title()

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

    def on_menuitem_project_new_activate(self, item):
        #self.project_filename = None
        pass

    def on_menuitem_project_open_activate(self, item):
        self.on_open_clicked(item)

    def on_menuitem_project_save_activate(self, item):
        self.on_save_clicked(item)

    def on_menuitem_project_saveas_activate(self, item):
        self.on_save_clicked(item, True)

    def on_menuitem_app_quit_activate(self, item):
        self.quit()

    def set_editor_widget(self, widget):
        self.editortextview = widget
        #self.grid.attach(self.editortextview, 1, 1, 2, 1)

if __name__ == "__main__":
    app = NotebookApp()
    app.run(sys.argv)

