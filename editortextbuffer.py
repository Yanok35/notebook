#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, Gtk, Pango

class EditorTextBuffer(Gtk.TextBuffer):
    __gtype_name__ = 'EditorTextBuffer'

    def __init__(self):
        Gtk.TextBuffer.__init__(self)

        self.tag_bold = self.create_tag("bold",
            weight=Pango.Weight.BOLD)
        self.tag_italic = self.create_tag("italic",
            style=Pango.Style.ITALIC)
        self.tag_underline = self.create_tag("underline",
            underline=Pango.Underline.SINGLE)

    def get_tag_bold(self):
        return self.tag_bold

    def get_tag_italic(self):
        return self.tag_italic

    def get_tag_underline(self):
        return self.tag_underline

    # def on_apply_tag(self, widget, tag):
    #     bounds = self.textbuffer.get_selection_bounds()
    #     if len(bounds) != 0:
    #         start, end = bounds
    #         self.textbuffer.apply_tag(tag, start, end)

    # def on_remove_all_tags(self, widget):
    #     bounds = self.textbuffer.get_selection_bounds()
    #     if len(bounds) != 0:
    #         start, end = bounds
    #         self.textbuffer.remove_all_tags(start, end)

    # def on_justify_toggled(self, widget, justification):
    #     self.textview.set_justification(justification)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = f.read()
            self.set_text("")
            format = self.register_deserialize_tagset()
            self.deserialize(self, format, self.get_end_iter(), data)

    def save_to_file(self, filename):
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        format = self.register_serialize_tagset()
        text = self.serialize(self, format, start_iter, end_iter)
        with open(filename, 'w') as f:
            f.write(text)

    def insert_pixbuf_at_cursor(self, pixbuf):
        mark = self.get_mark('insert')
        cur_iter = self.get_iter_at_mark(mark)
        self.insert_pixbuf(cur_iter, pixbuf)

