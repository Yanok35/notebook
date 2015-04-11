#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import copy

from gi.repository import Gdk, Gtk, GtkSource, Pango

from ielementblock import *
from editortextbuffer import EditorTextBuffer
from xrefwin import XRefWin

class EditorTextView(GtkSource.View, ElementBlockInterface):
    __gtype_name__ = 'EditorTextView'

    __gsignals__ = copy.copy(ElementBlockInterface.__gsignals__)

    # 'Static' class members
    bold_btn = None
    ital_btn = None
    unde_btn = None
    code_btn = None
    xref_btn = None

    accel_grp = None

    # toolbar handling using class methods
    @classmethod
    def toolbar_create(cls, toolbar, self):
        if cls.bold_btn is None:
            cls.bold_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_BOLD)
            cls.bold_btn.set_tooltip_text('Set selection to bold')
            toolbar.insert(cls.bold_btn, -1)

        if cls.ital_btn is None:
            cls.ital_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_ITALIC)
            cls.ital_btn.set_tooltip_text('Set selection to italic')
            toolbar.insert(cls.ital_btn, -1)

        if cls.unde_btn is None:
            cls.unde_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_UNDERLINE)
            cls.unde_btn.set_tooltip_text('Underline selected chars')
            toolbar.insert(cls.unde_btn, -1)

        if cls.code_btn is None:
            cls.code_btn = Gtk.ToolButton()
            img = Gtk.Image.new_from_file("icons/code-inline-icon.svg")
            cls.code_btn.set_icon_widget(img)
            cls.code_btn.set_tooltip_text('Switch selected chars to verbatim mode')
            toolbar.insert(cls.code_btn, -1)

        if cls.xref_btn is None:
            #img = Gtk.Image.new_from_file("icons/block-del.svg")
            #cls.xref_btn = Gtk.ToolButton()
            #cls.xref_btn.set_icon_widget(img)
            cls.xref_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_EXECUTE)
            cls.xref_btn.set_tooltip_text('Add a cross-reference in block')
            cls.xref_btn.show_all()
            toolbar.insert(cls.xref_btn, -1)

        cls.bold_btn.connect('clicked', self.on_bold_button_clicked)
        cls.ital_btn.connect('clicked', self.on_italic_button_clicked)
        cls.unde_btn.connect('clicked', self.on_underline_button_clicked)
        cls.code_btn.connect('clicked', self.on_code_button_clicked)
        cls.xref_btn.connect('clicked', self.on_xref_button_clicked)

    @classmethod
    def toobar_set_visible(cls, visible):
        for w in [ cls.bold_btn, cls.ital_btn, cls.unde_btn, cls.code_btn ]:
            if visible:
                w.show()
            else:
                w.hide()

    def __init__(self, elements_toolbar, **args):
        GtkSource.View.__init__(self, **args)

        self.set_size_request(400, -1)

        self.set_hexpand(True)
        #self.set_vexpand(True)

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

        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drag_dest_add_text_targets()
        #self.connect("drag-data-received", self.on_drag_data_received)

        # img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        # vp = Gtk.Viewport()
        # vp.add(img)
        # self.image = vp
        # self.image.show()

        # self.add(self.image)

        EditorTextView.toolbar_create(elements_toolbar, self)

    def do_drag_data_received(self, context, x, y, selection_data, info, time_):
    #def on_drag_data_received(self, context, x, y, selection_data, info, time_):
        print('do_drag_data_received', context, x, y, info)
        #if info == 0: #TARGET_ENTRY_TEXT:
        text = selection_data.get_text()
        print("DND Received text: %s" % text)

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
                    self.emit('cursor-move', ElementBlockInterface.CursorDirection.UP)
                    return True
            elif key == 'Down':
                next_line = cur_iter.copy()
                possible = self.forward_display_line(next_line)
                if not possible:
                    print("last line : should change block + 1, pos %d" % cur_iter.get_line_offset())
                    self.emit('cursor-move', ElementBlockInterface.CursorDirection.DOWN)
                    return True
        else:
            pass #print(key)

        ## #print("key_press_event in editortextview")
        retval = GtkSource.View.do_key_press_event(self, event)
        #print ("   %s" % str(retval))
        return retval

    def do_parent_set(self, oldparent):
        toplevel = self.get_toplevel()
        if EditorTextView.accel_grp is None and toplevel.is_toplevel():
            EditorTextView.accel_grp = Gtk.AccelGroup()
            toplevel.add_accel_group(EditorTextView.accel_grp)

            key, mod = Gtk.accelerator_parse("<Control>b")
            EditorTextView.bold_btn.add_accelerator('clicked', EditorTextView.accel_grp, key, mod, Gtk.AccelFlags.VISIBLE)
            key, mod = Gtk.accelerator_parse("<Control>i")
            EditorTextView.ital_btn.add_accelerator('clicked', EditorTextView.accel_grp, key, mod, Gtk.AccelFlags.VISIBLE)
            key, mod = Gtk.accelerator_parse("<Control>u")
            EditorTextView.unde_btn.add_accelerator('clicked', EditorTextView.accel_grp, key, mod, Gtk.AccelFlags.VISIBLE)

    def on_bold_button_clicked(self, btn):
        if self.is_focus():
            buf = self.get_buffer()
            buf.tag_toggle_on_selection_bound(buf.get_tag_bold())

    def on_italic_button_clicked(self, btn):
        if self.is_focus():
            buf = self.get_buffer()
            buf.tag_toggle_on_selection_bound(buf.get_tag_italic())

    def on_underline_button_clicked(self, btn):
        if self.is_focus():
            buf = self.get_buffer()
            buf.tag_toggle_on_selection_bound(buf.get_tag_underline())

    def on_code_button_clicked(self, btn):
        if self.is_focus():
            buf = self.get_buffer()
            buf.tag_toggle_on_selection_bound(buf.get_tag_code())

    def on_xref_button_clicked(self, btn):
        if self.is_focus():
            print('on_xref_clicked')
            w = XRefWin.get_instance()
            #if not self.model:
            #    self.model = ImageModel() ???
            #w.set_model(self.model)
            if not w.is_visible():
                w.show_all()

                # Move window near the main window app
                parent = self.get_parent_window().get_effective_parent()
                _dont_care_, parent_x, parent_y = parent.get_origin()
                parent_w = parent.get_width()
                parent_h = parent.get_height()

                w.move(parent_x + parent_w, parent_y)

    def on_justify_toggled(self, widget, justification):
        self.textview.set_justification(justification)

    # ElementBlockInterface implementation
    def get_content_as_html(self):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.get_content_as_html()

    def get_content_as_text(self):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.get_content_as_text()

    def set_element_serialized(self, data):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.set_element_serialized(data)

    def get_element_serialized(self):
        buf = self.get_buffer()
        assert(buf is not None)
        return buf.get_element_serialized()

    def get_serialize_tag_name(self):
        return 'p'

    def is_deletable(self):
        buf = self.get_buffer()
        start = buf.get_start_iter()
        end = buf.get_end_iter()
        return start.compare(end) == 0

    def get_pages_required_for_rendering(self, w, h):
        print('get_pages_required_for_rendering', w, h)
        mini_w, natural = self.get_preferred_width()
        mini_h, natural = self.get_preferred_height()
        print(' widget needs :', mini_w, mini_h)
        return 1

    def draw_on_cairo_surface(self, ctx, x, y, w, h, part_number = 0):
        mini_w, natural = self.get_preferred_width()
        mini_h, natural = self.get_preferred_height()

        ctx.save()
        ctx.translate(x, y) # to match Gtk absolute coord
        GtkSource.View.do_draw(self, ctx)
        ctx.restore()

        return mini_w, mini_h

