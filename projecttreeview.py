#!/usr/bin/env python

from gi.repository import Gdk, GObject, Gtk, Pango

class ProjectTreeView(Gtk.VBox):

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.treestore = Gtk.TreeStore(GObject.TYPE_STRING)
        self.treestore.connect("row-inserted", self.on_treemodel_row_inserted)
        self.treestore.connect("row-deleted", self.on_treemodel_row_deleted)
        self.treestore.connect("row-changed", self.on_treemodel_row_changed)

        self.treeview = Gtk.TreeView.new_with_model(self.treestore)
        self.treeview.expand_all()
        self.treeview.set_reorderable(True)
        self.treeview.set_activate_on_single_click(True)

        sel = self.treeview.get_selection()
        sel.set_mode(Gtk.SelectionMode.MULTIPLE)
        sel.connect("changed", self.on_treeview_selection_changed)

        column_title = ['Document name']
        for i in range(0, 1):
            renderer = Gtk.CellRendererText()
            renderer.connect("edited", self.on_treeview_cell_edited)
            renderer.set_property("editable", True)
            column = Gtk.TreeViewColumn(column_title[i], renderer, text=i)
            self.treeview.append_column(column)

        self.treeview.connect('key-press-event', self.on_treeview_key_press_event)

        toolbar = Gtk.Toolbar()
        self.button_add_doc = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ADD)
        self.button_add_doc.connect("clicked", self.on_button_add_doc_clicked)
        self.button_del_doc = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
        self.button_del_doc.set_sensitive(False)
        self.button_del_doc.connect("clicked", self.on_button_del_doc_clicked)
        toolbar.insert(self.button_add_doc, 0)
        toolbar.insert(self.button_del_doc, 1)
        toolbar.insert(Gtk.SeparatorToolItem(), 2)
        self.pack_start(toolbar, False, False, 0)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.pack_start(self.scrolledwindow, True, True, 0)
        self.show_all()

    def load_from_file(self, filename):
        print("user asked to load project from ", filename)
        pass

    def save_to_file(self, filename):
        print("user asked to save project to ", filename)
        pass

    def on_button_add_doc_clicked(self, widget):
        treesel = self.treeview.get_selection()
        store, sel_list = treesel.get_selected_rows()
        if len(sel_list) == 0:
            path = Gtk.TreePath.new_from_string('0')
            row_pos = -1
        elif len(sel_list) == 1:
            path = sel_list[0]
            row_pos = int(str(path)[str(path).rfind(':') + 1:])

        #print ("add new doc at", str(path))
        #print ("row_pos", str(row_pos))

        parent = None
        if len(sel_list) == 1:
            iter_sel = self.treestore.get_iter(path)
            superpath = path.copy()
            if superpath.up() and superpath.get_depth() > 0:
                parent = self.treestore.get_iter(superpath)

        iter_new = self.treestore.insert(parent, row_pos+1)
        self.treestore.set_value(iter_new, 0, "<Write your title>")

    def on_button_del_doc_clicked(self, widget):
        treesel = self.treeview.get_selection()
        store, sel_list = treesel.get_selected_rows()
        if len(sel_list) > 1:
            print("todo: ask user for confirmation")
            return
        for path in sel_list:
            print ("remove doc at", str(path))
            iter = self.treestore.get_iter(path)
            self.treestore.remove(iter)
            # warning: after remove is called, all path in sel_list
            # are not valid anymore... to fixup

    def on_treemodel_row_inserted(self, treemodel, path, iter):
        print ("row-inserted", str(path), iter)

    def on_treemodel_row_deleted(self, treemodel, path):
        print ("row-deleted", str(path))

    def on_treemodel_row_changed(self, treemodel, path, iter):
        print ("row-changed", str(path), iter)

    def on_treeview_selection_changed(self, treesel):
        print("selection changed")
        treeview = treesel.get_tree_view()
        store, sel_list = treesel.get_selected_rows()
        if len(sel_list) == 0:
            self.button_del_doc.set_sensitive(False)
        else:
            self.button_del_doc.set_sensitive(True)

        if len(sel_list) > 1:
            self.button_add_doc.set_sensitive(False)
        else:
            self.button_add_doc.set_sensitive(True)

        for treepath in sel_list:
            print (str(treepath))

    def on_treeview_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)
        # debug string :
        #print(key + str(event.state))

        if key == 'F3':
            treesel = self.treeview.get_selection()
            store, sel_list = treesel.get_selected_rows()
            #for treepath in sel_list:
            #    print (str(treepath))
            if len(sel_list) == 1:
                print("start edit", str(sel_list[0]))
                self.treeview.set_cursor(sel_list[0], start_editing=True)
                return True
        return False

    def on_treeview_cell_edited(self, cell_renderer, path, new_text):
        print ("cell edited", str(path), " => ", new_text)
        iter = self.treestore.get_iter(path)
        self.treestore.set_value(iter, 0, new_text)
        #treestore = self.treeview.get_model()

