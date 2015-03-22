#!/usr/bin/env python

from gi.repository import Gdk, GObject, Gtk, Pango

class ProjectTreeView(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.treestore = Gtk.TreeStore(GObject.TYPE_STRING)
        iter = self.treestore.append(None, ['Premier chapitre'])
        iter2 = self.treestore.append(iter, ['1.1'])
        iter2 = self.treestore.append(iter, ['1.2'])
        iter2 = self.treestore.append(iter, ['1.3'])
        iter = self.treestore.append(None, ['Deuxieme chapitre'])
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

        self.add(self.treeview)
        self.show_all()

    def load_from_file(self, filename):
        print("user asked to load project from ", filename)
        pass

    def save_to_file(self, filename):
        print("user asked to save project to ", filename)
        pass

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

