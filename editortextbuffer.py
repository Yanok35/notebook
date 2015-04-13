#!/usr/bin/env python
# -*- coding: utf8 -*-

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Unicode support
from __future__ import unicode_literals

import binascii

from gi.repository import Gdk, Gtk, GtkSource, Pango
from lxml import etree

class AttribTextTag(Gtk.TextTag):

    def __init__(self, **args):
        Gtk.TextTag.__init__(self, **args)
        self._properties = args
        self._attribs = {}

    # Serialize
    def tostring(self):
        root_node = etree.Element('attribtexttag')
        tagtree = etree.ElementTree(root_node)

        parentnode = etree.SubElement(root_node, 'properties')
        for key, value in self._properties.items():
            node = etree.SubElement(parentnode, key)
            node.text = str(value)
            #node.attrib["href"] = binascii.hexlify(url)

        parentnode = etree.SubElement(root_node, 'attributes')
        for key, value in self._attribs.items():
            node = etree.SubElement(parentnode, key)
            node.text = value

        text = etree.tostring(tagtree, pretty_print=True)
        return text

    # Deserialize and create instance
    @classmethod
    def fromstring(cls, data):
        args = {}

        doc = etree.fromstring(data)
        parentnode = doc.find('properties')
        for prop in parentnode:
            if prop.text == "True":
                args[prop.tag] = True
            elif prop.text == "False":
                args[prop.tag] = False
            else:
                args[prop.tag] = prop.text

        tag = cls(**args)

        parentnode = doc.find('attributes')
        for prop in parentnode:
            tag._attribs[prop.tag] = prop.text

        return tag

    # Accessors
    def set_attribute(self, name, value):
        self._attribs[name] = value

    def get_attribute(self, name):
        return self._attribs[name]

class EditorTextBuffer(GtkSource.Buffer):
    __gtype_name__ = 'EditorTextBuffer'

    def __init__(self):
        GtkSource.Buffer.__init__(self)

        self.set_highlight_matching_brackets(False)
        self.buf_internal_access = False

        self.html_tag_translation = {}

        self.tag_bold = self.create_tag("bold",
            weight=Pango.Weight.BOLD)
        self.tag_italic = self.create_tag("italic",
            style=Pango.Style.ITALIC)
        self.tag_underline = self.create_tag("underline",
            underline=Pango.Underline.SINGLE)
        self.tag_code = self.create_tag("code",
            family="Courier")

        self.html_tag_translation[self.tag_bold] = ["strong"]
        self.html_tag_translation[self.tag_italic] = ["em"]
        self.html_tag_translation[self.tag_underline] = ['span class="underline"', 'span']

        self.tag_readonly = self.create_tag("readonly",
            editable=False)
        self.tag_blue = self.create_tag("blue",
            foreground="blue")
        self.tag_font_serif = self.create_tag("family",
            family="Serif")
        self.tag_font_big = self.create_tag("big",
            size=20*Pango.SCALE)

        self.attr_tags_list = []

    def do_insert_text(self, pos, new_text, new_text_length):
        #print(pos, new_text)
        # if not self.buf_internal_access:
        #     # Protect user insertion before top title
        #     if pos.compare(self.get_start_iter()) == 0:
        #         print("dropped")
        #         return False

        return GtkSource.Buffer.do_insert_text(self, pos, new_text, new_text_length)

    def _buf_internal_access(self, access):
        if access:
            self.begin_not_undoable_action()
            self.buf_internal_access = True
        else:
            self.end_not_undoable_action()
            self.buf_internal_access = False

    def get_tag_bold(self):
        return self.tag_bold

    def get_tag_italic(self):
        return self.tag_italic

    def get_tag_underline(self):
        return self.tag_underline

    def get_tag_code(self):
        return self.tag_code

    def tag_toggle_on_selection_bound(self, tag):
        bounds = self.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            if start.begins_tag(tag) and end.ends_tag(tag):
                self.remove_tag(tag, start, end)
            else:
                self.apply_tag(tag, start, end)

    # def on_remove_all_tags(self, widget):
    #     bounds = self.textbuffer.get_selection_bounds()
    #     if len(bounds) != 0:
    #         start, end = bounds
    #         self.textbuffer.remove_all_tags(start, end)

    # def on_justify_toggled(self, widget, justification):
    #     self.textview.set_justification(justification)

    def get_content_as_html(self):
        iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        text = u''

        while iter.compare(end_iter) != 0:
            for tag in self.html_tag_translation.keys():
                if iter.begins_tag(tag):
                    html_tag = self.html_tag_translation[tag]
                    text += '<' + html_tag[0] + '>'

            new_char = iter.get_char().decode('utf-8')
            if new_char == '\n':
                text += u'<br/>'
            text += new_char.encode('ascii', errors='xmlcharrefreplace')
            iter.forward_char()

            for tag in list(reversed(self.html_tag_translation.keys())):
                if iter.ends_tag(tag):
                    html_tag = self.html_tag_translation[tag]
                    text += '</' + html_tag[len(html_tag)-1] + '>'

        #import lxml.html
        #html = lxml.html.fromstring(text)
        #text = lxml.html.tostring(html, pretty_print=True)
        return text

    def get_content_as_text(self):
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        include_hidden_chars = False
        return self.get_text(start_iter, end_iter, include_hidden_chars)

    def set_element_serialized(self, data):
        self._buf_internal_access(True)

        # Reset buffer content
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        self.delete(start_iter, end_iter)

        # Catch etree as string
        doc = etree.fromstring(data)
        text_node = doc.find('hextext')

        # Unserialize all customs tags
        tags_node = doc.find('tags')
        for tag in tags_node:
            data = binascii.unhexlify(tag.text)

            tag = AttribTextTag.fromstring(data)
            tagtable = self.get_tag_table()
            tagtable.add(tag)
            self.attr_tags_list.append(tag)

        # Unserialize text data
        serformat = self.register_deserialize_tagset()
        text = binascii.unhexlify(text_node.text)
        self.deserialize(self, serformat, start_iter, text)

        self._buf_internal_access(False)

    def get_element_serialized(self):
        #print('get_content_as_html in textbuf')
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        serformat = self.register_serialize_tagset()

        root_node = etree.Element('textbuffer')
        tagtree = etree.ElementTree(root_node)

        text_node = etree.SubElement(root_node, 'hextext')
        output = binascii.hexlify(self.serialize(self, serformat, start_iter, end_iter))
        text_node.text = output

        tags_node = etree.SubElement(root_node, 'tags')

        for tag in self.attr_tags_list:
             node = etree.SubElement(tags_node, 'tag')
             node.text = binascii.hexlify(tag.tostring())

        return etree.tostring(tagtree, pretty_print = True)

    def insert_pixbuf_at_cursor(self, pixbuf):
        mark = self.get_mark('insert')
        cur_iter = self.get_iter_at_mark(mark)
        self.insert_pixbuf(cur_iter, pixbuf)

    def create_url_tag(self, text, url):
        tag_name = 'url%d' % len(self.attr_tags_list)
        tag = AttribTextTag(name = tag_name,
            editable=False, background='lightgrey')
        tag.set_attribute('text', text) # embedded for DND only
        tag.set_attribute('href', url)
        return tag

    def insert_attribtag_at_iter(self, iter, text, tag):
        tagtable = self.get_tag_table()
        tagtable.add(tag)
        self.attr_tags_list.append(tag)

        self.insert(iter, u' ')
        iter.forward_char()
        self.insert_with_tags(iter, text, tag)

    def remove_text_from_selection(self):
        print("remove_text_from_selection")
        start, end = self.get_selection_bounds()

        # If user want to delete a xref or url, it must exactly select the tag
        # in textview, otherwise the event is cancelled
        tag = False
        can_delete = True
        for tag in self.attr_tags_list:
            if start.has_tag(tag):
                in_tag = True
            #print(tag.get_property('name'), start.has_tag(tag), end.has_tag(tag))
            #print(tag.get_property('name'), start.begins_tag(tag), end.ends_tag(tag))
            if start.has_tag(tag) and (not (start.begins_tag(tag) and end.ends_tag(tag))):
                can_delete = False
                break

        if can_delete:
            self.delete(start, end)

            # Remove tag from taglist:
            if in_tag and tag in self.attr_tags_list:
                self.attr_tags_list.remove(tag)

