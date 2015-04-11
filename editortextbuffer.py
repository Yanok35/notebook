#!/usr/bin/env python
# -*- coding: utf8 -*-

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Unicode support
from __future__ import unicode_literals

import binascii

from gi.repository import Gdk, Gtk, GtkSource, Pango

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

        # Unserialize data
        serformat = self.register_deserialize_tagset()
        text = binascii.unhexlify(data)
        self.deserialize(self, serformat, start_iter, text)

        self._buf_internal_access(False)

    def get_element_serialized(self):
        print('get_content_as_html in textbuf')
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        serformat = self.register_serialize_tagset()
        return binascii.hexlify(self.serialize(self, serformat, start_iter, end_iter))

    def insert_pixbuf_at_cursor(self, pixbuf):
        mark = self.get_mark('insert')
        cur_iter = self.get_iter_at_mark(mark)
        self.insert_pixbuf(cur_iter, pixbuf)

