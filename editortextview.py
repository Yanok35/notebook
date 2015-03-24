#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, Gtk, Pango

class EditorTextView(Gtk.ScrolledWindow):

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_size_request(600, -1)

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.set_text("")
        self.add(self.textview)

        self.tag_bold = self.textbuffer.create_tag("bold",
            weight=Pango.Weight.BOLD)
        self.tag_italic = self.textbuffer.create_tag("italic",
            style=Pango.Style.ITALIC)
        self.tag_underline = self.textbuffer.create_tag("underline",
            underline=Pango.Underline.SINGLE)

    def get_tag_bold(self):
        return self.tag_bold

    def get_tag_italic(self):
        return self.tag_italic

    def get_tag_underline(self):
        return self.tag_underline

    def on_apply_tag(self, widget, tag):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.apply_tag(tag, start, end)

    def on_remove_all_tags(self, widget):
        bounds = self.textbuffer.get_selection_bounds()
        if len(bounds) != 0:
            start, end = bounds
            self.textbuffer.remove_all_tags(start, end)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = f.read()
            self.textbuffer.set_text("")
            emptyBuffer = self.textbuffer
            format = emptyBuffer.register_deserialize_tagset()
            self.textbuffer.deserialize(emptyBuffer,
                format, emptyBuffer.get_end_iter(), data)

    def save_to_file(self, filename):
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        format = self.textbuffer.register_serialize_tagset()
        text = self.textbuffer.serialize(self.textbuffer,
            format, start_iter, end_iter)
        with open(filename, 'w') as f:
            f.write(text)

    def insert_pixbuf_at_cursor(self, pixbuf):
        mark = self.textbuffer.get_mark('insert')
        cur_iter = self.textbuffer.get_iter_at_mark(mark)
        self.textbuffer.insert_pixbuf(cur_iter, pixbuf)

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        # debug string :
        #print(key + str(event.state))

        if event.state & Gdk.ModifierType.CONTROL_MASK and key in ('o', 's', 'v'):
            if key == 'o':
                self.on_open_clicked(None)
            elif key == 's':
                self.on_save_clicked(None)
            elif key == 'v':
                pixbuf = self.clipboard.wait_for_image()
                if pixbuf != None:
                    mark = self.textbuffer.get_mark('insert')
                    cur_iter = self.textbuffer.get_iter_at_mark(mark)
                    self.textbuffer.insert_pixbuf(cur_iter, pixbuf)
                else:
                    return False

            #print ('event catched')
            return True

        return False

