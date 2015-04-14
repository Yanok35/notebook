#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Unicode support
from __future__ import unicode_literals

import os

from gi.repository import Gdk, GObject, Gtk, Pango
from lxml import etree

class ProjectTreeStore(Gtk.TreeStore):
    __gtype_name__ = str("ProjectTreeStore")

    __gsignals__ = {
        str('subdoc-inserted'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        str('subdoc-deleted'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        str('subdoc-changed'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
        str('subdoc-load-from-file'): (GObject.SIGNAL_RUN_FIRST, None, (int, str)),
        str('subdoc-save-to-file'): (GObject.SIGNAL_RUN_FIRST, None, (int, str)),
        #str('subdoc-order-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()), # list of ids to retreive
        #str('subdoc-selection-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()),

        #str('project-export'): (GObject.SIGNAL_RUN_FIRST, None, ()),
        #str('render-to-pdf'): (GObject.SIGNAL_RUN_FIRST, None, ()),
        #str('export-to-html'): (GObject.SIGNAL_RUN_FIRST, None, ()),
    }

    class Column:
        Types = [ GObject.TYPE_STRING, GObject.TYPE_INT, GObject.TYPE_STRING ]
        TITLE = 0 # User entry: string of (sub)section title
        DOCID = 1 # Generated : int of subdoc unique index
        SECT  = 2 # Generated : string of (sub)section id (ie. "1.3")

    def __init__(self):
        Gtk.TreeStore.__init__(self, *ProjectTreeStore.Column.Types)

        self.treestore = self # FIXME : to remove after cleanup
        #self.sigid_row_inserted = self.treestore.connect("row-inserted", self.on_treemodel_row_inserted)
        #self.sigid_row_deleted = self.treestore.connect("row-deleted", self.on_treemodel_row_deleted)
        #self.sigid_row_changed = self.treestore.connect("row-changed", self.on_treemodel_row_changed)

        self.subdocs_id = 0

    def _get_new_docid(self):
        self.subdocs_id += 1
        return self.subdocs_id

    def _rec_treestore_set_docs(self, iter, elem, filesdir):

        #print(type(elem.text), elem.text.__class__.__name__)
        if elem.text.__class__.__name__ != 'unicode':
            name = unicode(elem.text, encoding='utf-8')
        else:
            name = elem.text
        docid = int(elem.attrib["id"])
        iter_elem = self.treestore.append(iter, [elem.text, docid, ""])
        sectname = self.treestore.get_section_number_from_path(self.treestore.get_path(iter_elem))
        self.treestore.set_value(iter_elem, ProjectTreeStore.Column.SECT, sectname)
        #print (elem.text)

        # Create a new subdocument from file
        filename = os.path.join(filesdir, str(docid) + ".subdoc")
        self.emit('subdoc-inserted', docid)
        self.emit('subdoc-load-from-file', docid, str(filename))

        # Parse node's child if they exists
        subdoc_list = elem.findall('subdoc')
        for subdoc in subdoc_list:
            self._rec_treestore_set_docs(iter_elem, subdoc, filesdir)

    def load_from_file(self, filename):
        #print("user asked to load project from ", filename)
        #print(os.path.basename(filename))
        doc = etree.parse(filename)

        # todo: check file is in good format...
        # Check files dir exists
        filesdir = filename + ".files"
        if not os.path.exists(filesdir):
            raise ValueError

###        self.treestore.handler_block(self.sigid_row_inserted)
###        self.treestore.handler_block(self.sigid_row_deleted)
###        self.treestore.handler_block(self.sigid_row_changed)
        #self.treeselection.handler_block(self.sigid_treeselection_changed)
        
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
            self._rec_treestore_set_docs(None, subdoc, filesdir)

        #self.treeselection.handler_unblock(self.sigid_treeselection_changed)
###        self.treestore.handler_unblock(self.sigid_row_changed)
###        self.treestore.handler_unblock(self.sigid_row_deleted)
###        self.treestore.handler_unblock(self.sigid_row_inserted)

        # Parse XML file to find selection list
        docid_list = []
        selnode = doc.find('selection')
        subdoc_sel_list = selnode.findall('docid')
        for docid in subdoc_sel_list:
            docid_list.append(int(docid.text))

        #if len(subdoc_list) > 0:
        #    self.emit('subdoc-order-changed')

        return docid_list

    def _rec_treestore_get_docs(self, iter, elem, filesdir):
        docname = unicode(self.treestore.get_value(iter, ProjectTreeStore.Column.TITLE), encoding='utf-8')
        docid = unicode(self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID))

        node = etree.SubElement(elem, 'subdoc')
        node.text = docname
        node.attrib["id"] = docid

        # Catch content of subdoc[docid] and save to file
        filename = os.path.join(filesdir, str(docid)+".subdoc")
        print("doc id ", docid, " save to ", filename)
        self.emit('subdoc-save-to-file', int(docid), str(filename))

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            self._rec_treestore_get_docs(child, node, filesdir)

        return node

    def save_to_file(self, filename, sel_list):
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
            self._rec_treestore_get_docs(iter, treeview_node, filesdir)
            iter = self.treestore.iter_next(iter)

        #sel_list = self.get_selection_list()
        #raise NotImplementedError

        sel_node = etree.SubElement(projet, 'selection')
        if sel_list:
            for docid in sel_list:
                node = etree.SubElement(sel_node, 'docid')
                node.text = str(docid)

        outfile = open(filename, 'w')
        doc.write(outfile, pretty_print=True)

    def _rec_find_subdociter_from_id(self, iter, docid):
        #docname = unicode(self.treestore.get_value(iter, ProjectTreeStore.Column.TITLE), encoding='utf-8')
        elem_docid = int(self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID))
        if elem_docid == docid:
            return iter

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            child_iter = self._rec_find_subdociter_from_id(child, docid)
            if child_iter:
                return child_iter

        return None

    def find_subdociter_from_id(self, docid):
        elem_iter = None

        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            elem_iter = self._rec_find_subdociter_from_id(iter, docid)
            if elem_iter is not None:
                break
            iter = self.treestore.iter_next(iter)

        return elem_iter

    def _rec_treestore_get_doc_list(self, iter):
        retlist = []

        docname = unicode(self.treestore.get_value(iter, ProjectTreeStore.Column.TITLE), encoding='utf-8')
        docid = int(self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID))

        retlist.append([docid, docname])

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            childlist = self._rec_treestore_get_doc_list(child)
            for child in childlist:
                retlist.append(child)

        return retlist

    def get_doc_list(self):
        retlist = []

        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            childlist = self._rec_treestore_get_doc_list(iter)

            for child in childlist:
                retlist.append(child)

            iter = self.treestore.iter_next(iter)

        #print(retlist)
        return retlist

    def get_docid_list(self):
        retlist = []
        doclist = self.get_doc_list()
        for doc in doclist:
            retlist.append(doc[0])
        return retlist

    def _rec_get_docid_level(self, iter, docid):

        curid = int(self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID))
        if curid == docid:
            return self.treestore.iter_depth(iter)

        level = -1
        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            level = self._rec_get_docid_level(child, docid)
            if level != -1:
                break

        return level

    def get_docid_level(self, docid):

        level = -1
        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            level = self._rec_get_docid_level(iter, docid)
            if level != -1:
                return level
            iter = self.treestore.iter_next(iter)

        return level

    def get_section_number_from_path(self, path):
        text = u''
        tokens = str(path).split(':')
        for t in tokens:
            text += str(int(t) + 1)
            text += u'.'
        text = text[:-1]
        return text

    def _rec_get_iter_from_docid(self, iter, docid):
        iter_found = None
        #path = self.treestore.get_path(iter)
        if docid == self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID):
            iter_found = iter.copy()
            return iter_found

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            iter_found = self._rec_get_iter_from_docid(child, docid)
            if iter_found is not None:
                break
        return iter_found

    def get_iter_from_docid(self, docid):
        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            iter_found = self._rec_get_iter_from_docid(iter, docid)
            if iter_found is not None:
                break
            iter = self.treestore.iter_next(iter)

        return iter_found

    def get_section_number_from_docid(self, docid):
        iter = self.get_iter_from_docid(docid)
        return self.treestore.get_value(iter, ProjectTreeStore.Column.SECT)

    def subdoc_add_new(self, path, row_pos):

        #print ("add new doc at", str(path))
        #print ("row_pos", str(row_pos))

        parent = None
        if str(path) != "0":
            iter_sel = self.treestore.get_iter(path)
            superpath = path.copy()
            if superpath.up() and superpath.get_depth() > 0:
                parent = self.treestore.get_iter(superpath)

        iter_new = self.treestore.insert(parent, row_pos+1)
        path_new = self.treestore.get_path(iter_new)

        # Create a new subdocument
        docid = self._get_new_docid()

        # Add an entry in project's treeview
        self.treestore.set_value(iter_new, ProjectTreeStore.Column.TITLE, "<Write your title>")
        self.treestore.set_value(iter_new, ProjectTreeStore.Column.DOCID, docid)
        self.treestore.set_value(iter_new, ProjectTreeStore.Column.SECT,
                                 self.treestore.get_section_number_from_path(path_new))
        self.emit('subdoc-inserted', docid)

    def subdoc_del(self, path):
        #print ("remove doc at", str(path))
        iter = self.treestore.get_iter(path)
        docid = self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID)
        self.treestore.remove(iter)
        self.emit('subdoc-deleted', docid)
        #self.emit('subdoc-changed', docid)
        # FIXME: after remove is called, all path in sel_list
        # are not valid anymore... to fixup

    def subdoc_set_title(self, path, new_text):
        iter = self.treestore.get_iter(path)
        self.treestore.set_value(iter, ProjectTreeStore.Column.TITLE, new_text)

        docid = int(self.treestore.get_value(iter, ProjectTreeStore.Column.DOCID))
        self.emit('subdoc-changed', docid)

    def _rec_refresh_all_section_number(self, iter):

        path = self.treestore.get_path(iter)
        self.treestore.set_value(iter, ProjectTreeStore.Column.SECT,
                                 self.treestore.get_section_number_from_path(path))

        for i in range(0, self.treestore.iter_n_children(iter)):
            child = self.treestore.iter_nth_child(iter, i)
            self._rec_refresh_all_section_number(child)

    def subdoc_refresh_all_section_number(self):

        iter = self.treestore.get_iter_first()
        while iter is not None and self.treestore.iter_is_valid(iter):
            self._rec_refresh_all_section_number(iter)
            iter = self.treestore.iter_next(iter)

    def do_treemodel_row_inserted(self, treemodel, path, iter):
        print ("row-inserted", str(path), iter)

    def do_treemodel_row_deleted(self, treemodel, path):
        print ("row-deleted", str(path))

    def do_treemodel_row_changed(self, treemodel, path, iter):
        print ("row-changed", str(path), iter)

GObject.type_register(ProjectTreeStore)

