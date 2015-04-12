#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Unicode support
from __future__ import unicode_literals

import os

from gi.repository import Gdk, GObject, Gtk, Pango
from lxml import etree

#from editortextview import EditorTextView
from projecttreestore import ProjectTreeStore

class PTreeView(Gtk.TreeView):
    def __init__(self):
        Gtk.TreeView.__init__(self)

    def do_drag_drop(self, context, x, y, time_):
        Gtk.TreeView.do_drag_drop(self, context, x, y, time_)
        return False

class ProjectTreeView(Gtk.Box):
    __gtype_name__ = str("ProjectTreeView")

    __gsignals__ = {
        str('subdoc-order-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()), # list of ids to retreive
        str('subdoc-selection-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()),

        str('project-export'): (GObject.SIGNAL_RUN_FIRST, None, ()),
        str('render-to-pdf'): (GObject.SIGNAL_RUN_FIRST, None, ()),
        str('export-to-html'): (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.treestore = None #ProjectTreeStore()

        self.treeview = PTreeView()
        #self.treeview.set_model(self.treestore)
        self.treeview.expand_all()
        self.treeview.set_reorderable(True)
        self.treeview.set_activate_on_single_click(True)
        self.treeview.set_enable_search(False)
        self.treeview.connect('drag-begin', self.on_treeview_drag_begin)
        self.treeview.connect_after('drag-drop', self.on_treeview_drag_drop)

        self.treeselection = self.treeview.get_selection()
        self.treeselection.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.current_sel_list = None
        self.sigid_treeselection_changed = self.treeselection.connect("changed", self.on_treeview_selection_changed)

        column_title = ['Document name', 'DocID']
        for i in range(0, len(column_title)):
            renderer = Gtk.CellRendererText()
            if i == 0:
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
        self.button_export_doc = Gtk.ToolButton.new_from_stock(Gtk.STOCK_EXECUTE)
        self.button_export_doc.connect("clicked", self.on_button_export_doc_clicked)
        self.button_render_to_pdf = Gtk.ToolButton.new_from_stock(Gtk.STOCK_PAGE_SETUP)
        self.button_render_to_pdf.connect("clicked", self.on_button_render_to_pdf_clicked)
        img = Gtk.Image.new_from_file("icons/export-html.svg")
        self.button_export_to_html = Gtk.ToolButton()
        self.button_export_to_html.set_icon_widget(img)
        self.button_export_to_html.connect("clicked", self.on_button_export_to_html_clicked)
        toolbar.insert(self.button_add_doc, -1)
        toolbar.insert(self.button_del_doc, -1)
        toolbar.insert(Gtk.SeparatorToolItem(), -1)
        #toolbar.insert(self.button_export_doc, -1)
        toolbar.insert(self.button_render_to_pdf, -1)
        toolbar.insert(self.button_export_to_html, -1)
        self.pack_start(toolbar, False, False, 0)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.pack_start(self.scrolledwindow, True, True, 0)
        self.show_all()

        self.subdocs_id = 0

    def set_model(self, model):
        self.treeview.set_model(model)
        self.treestore = model

    def get_model(self):
        return self.treestore

    def load_from_file(self, filename):
        docid_list = self.treestore.load_from_file(filename)
        self.set_selection_list(docid_list)
        self.treeview.expand_all()

    def save_to_file(self, filename):
        print("user asked to save project to ", filename)
        sel_list = self.get_selection_list()
        self.treestore.save_to_file(filename, sel_list)

    def get_selection_list(self):
        retlist = []
        if self.current_sel_list:
            for treepath in self.current_sel_list:
                iter = self.treestore.get_iter(treepath)
                docid = self.treestore.get_value(iter, 1)
                retlist.append(int(docid))
        return retlist
        #return self.current_sel_list

    def set_selection(self, docid):
        iter = self.treestore.find_subdociter_from_id(docid)
        if iter:
            self.treeselection.select_iter(iter)

    def set_selection_list(self, docid_list):
        self.treeselection.unselect_all()

        self.treeselection.handler_block(self.sigid_treeselection_changed)
        self.treeview.expand_all() # required to have the selection to occur !
        self.treeselection.set_mode(Gtk.SelectionMode.MULTIPLE)
        if docid_list and len(docid_list) > 0:
            for doc in docid_list:
                self.set_selection(doc)
        self.treeselection.handler_unblock(self.sigid_treeselection_changed)

        #self.current_sel_list = self.treeselection
        self.treeselection.emit('changed')

    def on_button_add_doc_clicked(self, widget):
        treesel = self.treeview.get_selection()
        store, sel_list = treesel.get_selected_rows()
        if len(sel_list) == 0:
            path = Gtk.TreePath.new_from_string('0')
            row_pos = -1
        elif len(sel_list) == 1:
            path = sel_list[0]
            row_pos = int(str(path)[str(path).rfind(':') + 1:])

        self.treestore.subdoc_add_new(path, row_pos)

    def on_button_del_doc_clicked(self, widget):
        treesel = self.treeview.get_selection()
        store, sel_list = treesel.get_selected_rows()
        if len(sel_list) > 1:
            print("todo: ask user for confirmation")
            return

        for path in sel_list:
            self.treestore.subdoc_del(path)

    def on_button_export_doc_clicked(self, widget):
        self.emit('project-export')

    def on_button_render_to_pdf_clicked(self, widget):
        self.emit('render-to-pdf')

    def on_button_export_to_html_clicked(self, widget):
        self.emit('export-to-html')

    def on_treeview_drag_begin(self, widget, context):
        store, path_list = self.treeselection.get_selected_rows()
        self.drag_treepath_begin = []
        for path in path_list:
            iter = self.treestore.get_iter(path)
            docid = int(self.treestore.get_value(iter, 1))
            self.drag_treepath_begin.append(docid)

    def on_treeview_drag_drop(self, widget, context, x, y, time):
        self.set_selection_list(self.drag_treepath_begin)
        return False

    def on_treeview_selection_changed(self, treesel):
        #print("selection changed")
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

        #for treepath in sel_list:
        #    print (str(treepath))

        # Reflect the selection on main app editor widget.
        if self.current_sel_list != sel_list:
            self.current_sel_list = sel_list
            self.emit('subdoc-selection-changed')

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

        # if event.state & Gdk.ModifierType.CONTROL_MASK and key in ('o', 's', 'v'):
        #     if key == 'o':
        #         self.load_from_file("projet.xml")
        return False

    def on_treeview_cell_edited(self, cell_renderer, path, new_text):
        new_text = unicode(new_text, encoding='utf-8')
        print ("cell edited", str(path), " => ", new_text)

        self.treestore.subdoc_set_title(path, new_text)

GObject.type_register(ProjectTreeView)

