#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Unicode support
from __future__ import unicode_literals

import os

from gi.repository import Gdk, GObject, Gtk, Pango
from lxml import etree

from editortextview import EditorTextView

class ProjectTreeView(Gtk.VBox):
    __gtype_name__ = 'ProjectTreeView'

    def __init__(self):
        Gtk.VBox.__init__(self)

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.treestore = Gtk.TreeStore(GObject.TYPE_STRING, GObject.TYPE_INT)
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

        column_title = ['Document name', 'DocID']
        for i in range(0, len(column_title)):
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

        self.subdocs_id = 0
        self.subdocs_refs = {}
        self.subdocs_vbox = Gtk.VBox()
        self.subdocs_empty_project = Gtk.Image.new_from_stock(Gtk.STOCK_DND, 64)
        self.subdocs_empty_project.set_size_request(600, -1)
        self.subdocs_vbox.pack_start(self.subdocs_empty_project, True, True, 0)

    def rec_treestore_set_docs(self, iter, elem, filesdir):

        #print(type(elem.text), elem.text.__class__.__name__)
        if elem.text.__class__.__name__ != 'unicode':
            name = unicode(elem.text, encoding='utf-8')
        else:
            name = elem.text
        docid = int(elem.attrib["id"])
        iter_elem = self.treestore.append(iter, [elem.text, docid])
        #print (elem.text)

        # Create a new subdocument from file
        filename = os.path.join(filesdir, str(docid)+".subdoc")
        editortextview = EditorTextView()
        editortextview.load_from_file(filename)
        self.subdocs_refs[docid] = (editortextview, filename)
        # Add widget to global VBox
        self.subdocs_vbox.pack_start(editortextview, True, True, 3)

        # Parse node's child if they exists
        subdoc_list = elem.findall('subdoc')
        for subdoc in subdoc_list:
            self.rec_treestore_set_docs(iter_elem, subdoc, filesdir)

    def load_from_file(self, filename):
        print("user asked to load project from ", filename)
        print(os.path.basename(filename))
        doc = etree.parse(filename)

        # todo: check file is in good format...
        # Check files dir exists
        filesdir = filename + ".files"
        if not os.path.exists(filesdir):
            raise ValueError

        # Remove previous doc in treeview
        self.treestore.clear()
        # Remove subdoc refs
        self.subdocs_id = 0
        self.subdocs_refs = {}

        # Parse XML file to add node recursively
        doctree = doc.find('doctree')
        self.subdocs_id = int(doctree.attrib["subdocs_id"])
        subdoc_list = doctree.findall('subdoc')
        for subdoc in subdoc_list:
            self.rec_treestore_set_docs(None, subdoc, filesdir)

        self.treeview.expand_all()

    def rec_treestore_get_docs(self, iter, elem, filesdir):
        docname = unicode(self.treestore.get_value(iter, 0), encoding='utf-8')
        docid = unicode(self.treestore.get_value(iter, 1))

        node = etree.SubElement(elem, 'subdoc')
        node.text = docname
        node.attrib["id"] = docid

        # Catch content of subdoc[docid] and save to file
        filename = os.path.join(filesdir, str(docid)+".subdoc")
        print("doc id ", docid, " save to ", filename)
        (editortextview, _dont_care_) = self.subdocs_refs[int(docid)]
        editortextview.save_to_file(filename)

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            self.rec_treestore_get_docs(child, node, filesdir)

        return node

    def save_to_file(self, filename):
        print("user asked to save project to ", filename)

        filesdir = filename + ".files"
        print(filesdir)
        if not os.path.exists(filesdir):
            os.mkdir(filesdir)

        projet = etree.Element('notebook_project')
        doc = etree.ElementTree(projet)

        treeview_node = etree.SubElement(projet, 'doctree')
        #treeview_node.text = "fichier 1"
        treeview_node.attrib["subdocs_id"] = unicode(self.subdocs_id)

        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            self.rec_treestore_get_docs(iter, treeview_node, filesdir)
            iter = self.treestore.iter_next(iter)

        outfile = open(filename, 'w')
        doc.write(outfile, pretty_print=True)

    def get_new_docid(self):
        self.subdocs_id += 1
        return self.subdocs_id

    def get_editor_widget(self):
        return self.subdocs_vbox

    def editor_update_widget_visibility(self, sel_list):
        print("propagate", len(self.subdocs_refs.items()))

        # fixme : remove and check widget are destroyed...
        self.subdocs_vbox.show_all()
        for (editortextview, filename) in self.subdocs_refs.values():
            editortextview.hide()

        if len(self.subdocs_refs.items()) == 0:
            self.subdocs_empty_project.show()
        else:
            self.subdocs_empty_project.hide()

            for spath in sel_list:
                print (str(spath))
                path = Gtk.TreePath(spath)
                iter = self.treestore.get_iter(path)
                docid = self.treestore.get_value(iter, 1)
                print(docid)
                (editortextview, filename) = self.subdocs_refs[docid]
                editortextview.show()
            # todo: refresh visible vbox...
            #self.app.set_editor_widget(self.subdocs_vbox)

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

        # Create a new subdocument
        docid = self.get_new_docid()
        editortextview = EditorTextView()
        #filename = editortextview.get_file_name(docid)
        filename = str(docid) + "-toto.txt"  # todo
        self.subdocs_refs[docid] = (editortextview, filename)

        # Add an entry in project's treeview
        self.treestore.set_value(iter_new, 0, "<Write your title>")
        self.treestore.set_value(iter_new, 1, docid)

        # Add widget to global VBox
        self.subdocs_vbox.pack_start(editortextview, True, True, 3)

    def on_button_del_doc_clicked(self, widget):
        treesel = self.treeview.get_selection()
        store, sel_list = treesel.get_selected_rows()
        if len(sel_list) > 1:
            print("todo: ask user for confirmation")
            return

        for path in sel_list:
            print ("remove doc at", str(path))
            iter = self.treestore.get_iter(path)
            docid = self.treestore.get_value(iter, 1)
            self.treestore.remove(iter)
            # warning: after remove is called, all path in sel_list
            # are not valid anymore... to fixup

            # remove entry in dictionary
            del self.subdocs_refs[docid]

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

        # Reflect the selection on main app editor widget.
        self.editor_update_widget_visibility(sel_list)

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
        new_text = unicode(new_text, encoding='utf-8')
        print ("cell edited", str(path), " => ", new_text)
        iter = self.treestore.get_iter(path)
        self.treestore.set_value(iter, 0, new_text)
        #treestore = self.treeview.get_model()

