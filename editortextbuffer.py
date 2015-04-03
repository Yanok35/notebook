#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, Gtk, GtkSource, Pango

class EditorTextBuffer(GtkSource.Buffer):
    __gtype_name__ = 'EditorTextBuffer'

    def __init__(self):
        GtkSource.Buffer.__init__(self)

        self.buf_internal_access = False

        self.tag_bold = self.create_tag("bold",
            weight=Pango.Weight.BOLD)
        self.tag_italic = self.create_tag("italic",
            style=Pango.Style.ITALIC)
        self.tag_underline = self.create_tag("underline",
            underline=Pango.Underline.SINGLE)
        self.tag_readonly = self.create_tag("readonly",
            editable=False)
        self.tag_blue = self.create_tag("blue",
            foreground="blue")
        self.tag_font_serif = self.create_tag("family",
            family="Serif")
        self.tag_font_big = self.create_tag("big",
            size=20*Pango.SCALE)

        self.title = unicode('')

    def do_insert_text(self, pos, new_text, new_text_length):
        #print(pos, new_text)
        if not self.buf_internal_access:
            # Protect user insertion before top title
            if pos.compare(self.get_start_iter()) == 0:
                print("dropped")
                return False

        return GtkSource.Buffer.do_insert_text(self, pos, new_text, new_text_length)

    def _buf_internal_access(self, access):
        if access:
            self.begin_not_undoable_action()
            self.buf_internal_access = True
        else:
            self.end_not_undoable_action()
            self.buf_internal_access = False

    def set_title(self, title):

        self._buf_internal_access(True)

        # remove previous title in buffer
        if len(self.title):
            start_iter = self.get_start_iter()
            end_iter = self.get_start_iter()
            end_iter.forward_chars(len(self.title))
            self.remove_all_tags(start_iter, end_iter)
            self.delete(start_iter, end_iter)

        if not title.endswith('\n'):
            title += '\n'

        start_iter = self.get_start_iter()
        self.insert(start_iter, title)

        start_iter = self.get_start_iter()
        end_iter = self.get_start_iter()
        end_iter.forward_chars(len(title))
        #print("len title=", len(title))

        self.apply_tag(self.tag_readonly, start_iter, end_iter)
        self.apply_tag(self.tag_underline, start_iter, end_iter)
        #self.apply_tag(self.tag_blue, start_iter, end_iter)
        self.apply_tag(self.tag_font_serif, start_iter, end_iter)
        self.apply_tag(self.tag_font_big, start_iter, end_iter)

        self._buf_internal_access(False)

        self.title = title

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
            self._buf_internal_access(True)
            self.set_text("")
            format = self.register_deserialize_tagset()
            self.deserialize(self, format, self.get_end_iter(), data)
            self._buf_internal_access(False)

    def save_to_file(self, filename):
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        format = self.register_serialize_tagset()
        text = self.serialize(self, format, start_iter, end_iter)
        with open(filename, 'w') as f:
            f.write(text)

    def get_content_as_text(self):
        start_iter = self.get_start_iter()
        end_iter = self.get_end_iter()
        include_hidden_chars = False
        return self.get_text(start_iter, end_iter, include_hidden_chars)

    def insert_pixbuf_at_cursor(self, pixbuf):
        mark = self.get_mark('insert')
        cur_iter = self.get_iter_at_mark(mark)
        self.insert_pixbuf(cur_iter, pixbuf)

