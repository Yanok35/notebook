#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, Gtk, GtkSource, Pango

from editortextbuffer import EditorTextBuffer

class EditorTextView(GtkSource.View):
    __gtype_name__ = 'EditorTextView'

    def __init__(self):
        GtkSource.View.__init__(self)

        self.set_size_request(600, -1)

        #self.set_hexpand(True)
        #self.set_vexpand(True)

        self.textbuffers = {} #EditorTextBuffer()
        self.textbuffer_visibleid = -1 # -1 means an image is displayed

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.textview = self
        #self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_justification(Gtk.Justification.FILL)

        #fontdesc = Pango.FontDescription("Monospace 11")
        fontdesc = Pango.FontDescription("Serif 12")
        self.textview.modify_font(fontdesc)
        #self.textview.set_show_line_numbers(True)
        #self.textview.set_highlight_current_line(True)

        ## Following works on Gtk.TextView only.
        #self.style_context = self.textview.get_style_context()
        #self.default_bg_color = self.style_context.get_background_color(Gtk.StateFlags.NORMAL)
        #self.textview.override_background_color(Gtk.StateFlags.NORMAL,
        #                                        Gdk.RGBA(0, 0, 0, 1))

        self.textview.connect('key-press-event', self.on_key_press_event)
        self.textview.show()

        # img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        # vp = Gtk.Viewport()
        # vp.add(img)
        # self.image = vp
        # self.image.show()

        # self.add(self.image)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

    #def subdoc_new(self, docid):
    #    self.textbuffers[docid] = EditorTextBuffer()

    def subdoc_set_visible(self, docid):
        #print(">>> set_visible = " + str(docid))
        # visid = self.textbuffer_visibleid
        # if visid == -1 and docid is not None:
        #     assert(self.textbuffers[docid] is not None)
        #     self.remove(self.image)
        #     self.add(self.textview)
        #     self.textbuffer_visibleid = docid
        # elif visid != -1 and docid is None:
        #     self.remove(self.textview)
        #     self.add(self.image)
        #     self.textbuffer_visibleid = -1

        if docid:
            assert(self.textbuffers[docid] is not None)
            #self.textview.set_buffer(self.textbuffers[docid])
            # self.textbuffer_visibleid = docid

    def load_from_file(self, filename):
        buf = self.get_buffer()
        assert(buf is not None)
        buf.load_from_file(filename)

    def save_to_file(self, filename):
        buf = self.get_buffer()
        assert(buf is not None)
        buf.save_to_file(filename)

    def set_title(self, title):
        buf = self.get_buffer()
        assert(buf is not None)
        buf.set_title(title)

    def get_content_as_text(self):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.get_content_as_text()

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        # debug string :
        #print(key + str(event.state))

        if event.state & Gdk.ModifierType.CONTROL_MASK and key in ('o', 's', 'v'):
            if key == 'v':
                pixbuf = self.clipboard.wait_for_image()
                visid = self.textbuffer_visibleid
                if pixbuf != None and visid != -1:
                    self.textbuffers[visid].insert_pixbuf_at_cursor(pixbuf)
                else:
                    return False

                #print ('event catched')
                return True

        return False

