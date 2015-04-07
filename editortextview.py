#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, Gtk, GtkSource, Pango

from ielementblock import ElementBlockInterface
from editortextbuffer import EditorTextBuffer

class EditorTextView(GtkSource.View, ElementBlockInterface):
    __gtype_name__ = 'EditorTextView'

    # 'Static' class members
    bold_btn = None
    ital_btn = None
    unde_btn = None

    # toolbar handling using class methods
    @classmethod
    def toolbar_create(cls, toolbar, self):
        if cls.bold_btn is None:
            cls.bold_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_BOLD)
            toolbar.insert(cls.bold_btn, -1)

        if cls.ital_btn is None:
            cls.ital_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ITALIC)
            toolbar.insert(cls.ital_btn, -1)

        if cls.unde_btn is None:
            cls.unde_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDERLINE)
            toolbar.insert(cls.unde_btn, -1)

        cls.bold_btn.connect('clicked', self.on_bold_button_clicked)
        cls.ital_btn.connect('clicked', self.on_italic_button_clicked)
        cls.unde_btn.connect('clicked', self.on_underline_button_clicked)

    @classmethod
    def toobar_set_visible(cls, visible):
        for w in [ cls.bold_btn, cls.ital_btn, cls.unde_btn ]:
            if visible:
                w.show()
            else:
                w.hide()

    def __init__(self, elements_toolbar):
        GtkSource.View.__init__(self)

        self.set_size_request(600, -1)

        self.set_hexpand(True)
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

        self.textview.show()

        # img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        # vp = Gtk.Viewport()
        # vp.add(img)
        # self.image = vp
        # self.image.show()

        # self.add(self.image)

        EditorTextView.toolbar_create(elements_toolbar, self)

    def do_focus_in_event(self, event):
        EditorTextView.toobar_set_visible(True)
        return GtkSource.View.do_focus_in_event(self, event)

    def do_focus_out_event(self, event):
        EditorTextView.toobar_set_visible(False)
        return GtkSource.View.do_focus_out_event(self, event)

    def do_key_press_event(self, event):
        key = Gdk.keyval_name(event.keyval)
        # # debug string :
        # print(event.keyval)
        # print(key + str(event.state), event.state)

        # Catch iter of the current cursor position
        buf = self.get_buffer()
        mark = buf.get_mark('insert')
        cur_iter = buf.get_iter_at_mark(mark)
        start_iter = buf.get_start_iter()
        end_iter = buf.get_end_iter()

        # Do not treat "Return" key normally... event is
        # up to subdocview container for block container addition
        if key == 'Return':
            if (event.state & Gdk.ModifierType.CONTROL_MASK) \
                or (event.state & Gdk.ModifierType.SHIFT_MASK) \
                or (event.state & Gdk.ModifierType.MOD1_MASK):
                    pass
            else:
                print('Return key-press-event is up to subdoc view...')
                return False
        elif key =='BackSpace' \
            and not buf.get_property('has-selection') \
            and cur_iter.compare(start_iter) == 0:
                print("Backspace! delete itself (if empty) and change block - 1, last_pos")
                print("or merge with block - 1, if previous is text")
                return False
        elif key in ('Up', 'Down', 'Left', 'Right'):
            #print("cur_iter (av move!) l %d : c %d" % (cur_iter.get_line(), cur_iter.get_line_index()))
            #print("  visible: l %d : c %d" % (cur_iter.get_line(), cur_iter.get_visible_line_index()))

            if key == 'Left' and cur_iter.compare(start_iter) == 0:
                print("start of buf : should change block - 1, last_pos")
            elif key == 'Right' and cur_iter.compare(end_iter) == 0:
                print("end of buf : should change block + 1, first_pos")
            elif key == 'Up':
                next_line = cur_iter.copy()
                possible = self.backward_display_line(next_line)
                if not possible:
                    print("first line : should change block - 1, pos %d" % cur_iter.get_line_offset())
                    return True
            elif key == 'Down':
                next_line = cur_iter.copy()
                possible = self.forward_display_line(next_line)
                if not possible:
                    print("last line : should change block + 1, pos %d" % cur_iter.get_line_offset())
                    return True
        else:
            pass #print(key)

        ## #print("key_press_event in editortextview")
        retval = GtkSource.View.do_key_press_event(self, event)
        #print ("   %s" % str(retval))
        return retval

    def on_bold_button_clicked(self, btn):
        if self.is_focus():
            print('on_bold_button_clicked')
            print(self)

    def on_italic_button_clicked(self, btn):
        if self.is_focus():
            print('on_italic_button_clicked')
            print(self)

    def on_underline_button_clicked(self, btn):
        if self.is_focus():
            print('on_underline_button_clicked')
            print(self)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

    # ElementBlockInterface implementation
    def get_content_as_text(self):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.get_content_as_text()

    def set_content_from_html(self, text):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.set_content_from_html(text)

    def get_content_as_html(self):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.get_content_as_html()

    def get_serialize_tag_name(self):
        return 'p'

    def is_deletable(self):
        buf = self.get_buffer()
        start = buf.get_start_iter()
        end = buf.get_end_iter()
        return start.compare(end) == 0






