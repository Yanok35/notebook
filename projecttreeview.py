#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Unicode support
from __future__ import unicode_literals

import os

from gi.repository import Gdk, GObject, Gtk, Pango
from lxml import etree

#from editortextview import EditorTextView

class PTreeView(Gtk.TreeView):
    def __init__(self):
        Gtk.TreeView.__init__(self)

    def do_drag_drop(self, context, x, y, time_):
        Gtk.TreeView.do_drag_drop(self, context, x, y, time_)
        return False

class ProjectTreeView(Gtk.Box):
    __gtype_name__ = str("ProjectTreeView")

    __gsignals__ = {
        str('subdoc-inserted'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        str('subdoc-deleted'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        str('subdoc-changed'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        str('subdoc-load-from-file'): (GObject.SIGNAL_RUN_FIRST, None, (int, str)),
        str('subdoc-save-to-file'): (GObject.SIGNAL_RUN_FIRST, None, (int, str)),
        str('subdoc-order-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()), # list of ids to retreive
        str('subdoc-selection-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()),

        str('project-export'): (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    def __init__(self):
        Gtk.Box.__init__(self)

        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.treestore = Gtk.TreeStore(GObject.TYPE_STRING, GObject.TYPE_INT)
        self.sigid_row_inserted = self.treestore.connect("row-inserted", self.on_treemodel_row_inserted)
        self.sigid_row_deleted = self.treestore.connect("row-deleted", self.on_treemodel_row_deleted)
        self.sigid_row_changed = self.treestore.connect("row-changed", self.on_treemodel_row_changed)

        self.treeview = PTreeView()
        self.treeview.set_model(self.treestore)
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
        toolbar.insert(self.button_add_doc, 0)
        toolbar.insert(self.button_del_doc, 1)
        toolbar.insert(Gtk.SeparatorToolItem(), 2)
        toolbar.insert(self.button_export_doc, 3)
        self.pack_start(toolbar, False, False, 0)

        self.scrolledwindow = Gtk.ScrolledWindow()
        self.scrolledwindow.add(self.treeview)
        self.pack_start(self.scrolledwindow, True, True, 0)
        self.show_all()

        self.subdocs_id = 0
        ### self.subdocs_refs = {}
        ### self.subdocs_vbox = Gtk.VBox()
        ### self.subdocs_empty_project = Gtk.Image.new_from_stock(Gtk.STOCK_DND, 64)
        ### self.subdocs_empty_project.set_size_request(600, -1)
        ### self.subdocs_vbox.pack_start(self.subdocs_empty_project, True, True, 0)

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
        filename = os.path.join(filesdir, str(docid) + ".subdoc")
        self.emit('subdoc-inserted', docid)
        self.emit('subdoc-load-from-file', docid, str(filename))

        ### editortextview = EditorTextView()
        ### editortextview.load_from_file(filename)
        ### self.subdocs_refs[docid] = (editortextview, filename)
        ### # Add widget to global VBox
        ### self.subdocs_vbox.pack_start(editortextview, True, True, 3)

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

        self.treestore.handler_block(self.sigid_row_inserted)
        self.treestore.handler_block(self.sigid_row_deleted)
        self.treestore.handler_block(self.sigid_row_changed)
        self.treeselection.handler_block(self.sigid_treeselection_changed)
        
        # Remove previous doc in treeview
        self.treestore.clear()
        # Remove subdoc refs
        self.subdocs_id = 0
        ### self.subdocs_refs = {}

        # Parse XML file to add node recursively
        doctree = doc.find('doctree')
        self.subdocs_id = int(doctree.attrib["subdocs_id"])
        subdoc_list = doctree.findall('subdoc')
        for subdoc in subdoc_list:
            self.rec_treestore_set_docs(None, subdoc, filesdir)

        self.treeselection.handler_unblock(self.sigid_treeselection_changed)
        self.treestore.handler_unblock(self.sigid_row_changed)
        self.treestore.handler_unblock(self.sigid_row_deleted)
        self.treestore.handler_unblock(self.sigid_row_inserted)

        # Parse XML file to find selection list
        docid_list = []
        selnode = doc.find('selection')
        subdoc_sel_list = selnode.findall('docid')
        for docid in subdoc_sel_list:
            docid_list.append(int(docid.text))

        if len(docid_list) > 0:
            self.set_selection_list(docid_list)

        if len(subdoc_list) > 0:
            self.emit('subdoc-order-changed')

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
        ### (editortextview, _dont_care_) = self.subdocs_refs[int(docid)]
        ### editortextview.save_to_file(filename)
        self.emit('subdoc-save-to-file', int(docid), str(filename))

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

        sel_list = self.get_selection_list()
        sel_node = etree.SubElement(projet, 'selection')
        if sel_list:
            for docid in sel_list:
                node = etree.SubElement(sel_node, 'docid')
                node.text = str(docid)

        outfile = open(filename, 'w')
        doc.write(outfile, pretty_print=True)

    def get_new_docid(self):
        self.subdocs_id += 1
        return self.subdocs_id

    def get_selection_list(self):
        retlist = []
        if self.current_sel_list:
            for treepath in self.current_sel_list:
                iter = self.treestore.get_iter(treepath)
                docid = self.treestore.get_value(iter, 1)
                retlist.append(int(docid))
        return retlist
        #return self.current_sel_list

    def rec_find_subdociter_from_id(self, iter, docid):
        #docname = unicode(self.treestore.get_value(iter, 0), encoding='utf-8')
        elem_docid = int(self.treestore.get_value(iter, 1))
        if elem_docid == docid:
            return iter

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            child_iter = self.rec_find_subdociter_from_id(child, docid)
            if child_iter:
                return child_iter

        return None

    def find_subdociter_from_id(self, docid):
        elem_iter = None

        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            elem_iter = self.rec_find_subdociter_from_id(iter, docid)
            if elem_iter is not None:
                break
            iter = self.treestore.iter_next(iter)

        return elem_iter

    def set_selection(self, docid):
        iter = self.find_subdociter_from_id(docid)
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

    def rec_treestore_get_doc_list(self, iter):
        retlist = []

        docname = unicode(self.treestore.get_value(iter, 0), encoding='utf-8')
        docid = int(self.treestore.get_value(iter, 1))

        retlist.append([docid, docname])

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            childlist = self.rec_treestore_get_doc_list(child)
            for child in childlist:
                retlist.append(child)

        return retlist

    def get_doc_list(self):
        retlist = []

        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            childlist = self.rec_treestore_get_doc_list(iter)

            for child in childlist:
                retlist.append(child)

            iter = self.treestore.iter_next(iter)

        print(retlist)
        return retlist

    def get_docid_list(self):
        retlist = []
        doclist = self.get_doc_list()
        for doc in doclist:
            retlist.append(doc[0])
        return retlist

###    def get_editor_widget(self):
###        return self.subdocs_vbox

###    def editor_update_widget_visibility(self, sel_list):
###        print("propagate", len(self.subdocs_refs.items()))
###
###        # fixme : remove and check widget are destroyed...
###        self.subdocs_vbox.show_all()
###        ### for (editortextview, filename) in self.subdocs_refs.values():
###        ###     editortextview.hide()
###
###        if len(self.subdocs_refs.items()) == 0:
###            self.subdocs_empty_project.show()
###        else:
###            self.subdocs_empty_project.hide()
###
###            for spath in sel_list:
###                print (str(spath))
###                path = Gtk.TreePath(spath)
###                iter = self.treestore.get_iter(path)
###                docid = self.treestore.get_value(iter, 1)
###                print(docid)
###                ### (editortextview, filename) = self.subdocs_refs[docid]
###                ### editortextview.show()
###            # todo: refresh visible vbox...
###            #self.app.set_editor_widget(self.subdocs_vbox)

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
        ### editortextview = EditorTextView()
        ### #filename = editortextview.get_file_name(docid)
        ### filename = str(docid) + "-toto.txt"  # todo
        ### self.subdocs_refs[docid] = (editortextview, filename)

        # Add an entry in project's treeview
        self.treestore.set_value(iter_new, 0, "<Write your title>")
        self.treestore.set_value(iter_new, 1, docid)
        self.emit('subdoc-inserted', docid)
        #self.emit('subdoc-changed', docid)

        # Add widget to global VBox
        ### self.subdocs_vbox.pack_start(editortextview, True, True, 3)
        

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
            self.emit('subdoc-deleted', docid)
            #self.emit('subdoc-changed', docid)
            # warning: after remove is called, all path in sel_list
            # are not valid anymore... to fixup

            ### # remove entry in dictionary
            ### del self.subdocs_refs[docid]

    def on_button_export_doc_clicked(self, widget):
        self.emit('project-export')

    def on_treemodel_row_inserted(self, treemodel, path, iter):
        print ("row-inserted", str(path), iter)

    def on_treemodel_row_deleted(self, treemodel, path):
        print ("row-deleted", str(path))

    def on_treemodel_row_changed(self, treemodel, path, iter):
        print ("row-changed", str(path), iter)

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
        ### self.editor_update_widget_visibility(sel_list)
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
        iter = self.treestore.get_iter(path)
        self.treestore.set_value(iter, 0, new_text)

        docid = int(self.treestore.get_value(iter, 1))
        self.emit('subdoc-changed', docid)

        #treestore = self.treeview.get_model()

