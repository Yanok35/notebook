#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#-*- coding: utf8 -*-

# Unicode support
from __future__ import unicode_literals

import cairo
from gi.repository import Gdk, Gtk, Pango, PangoCairo

from editortextbuffer import EditorTextBuffer

class EditorTextView(Gtk.ScrolledWindow):
    __gtype_name__ = 'EditorTextView'

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_size_request(600, -1)

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.textbuffers = {} #EditorTextBuffer()
        self.textbuffer_visibleid = -1 # -1 means an image is displayed

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        vp = Gtk.Viewport()
        darea = Gtk.DrawingArea()
        darea.set_size_request(800, 200)
        darea.set_can_focus(True)

        darea.connect('draw', self.on_draw)
        events  = Gdk.EventMask.ENTER_NOTIFY_MASK
        events |= Gdk.EventMask.KEY_PRESS_MASK
        darea.set_events(events)
        darea.connect('enter-notify-event', self.on_enter_notify_event)
        darea.connect('key-press-event', self.on_key_press_event)
#        darea.connect_after('realize', self.on_darea_realize)
##        vp.add(darea)
        #self.darea = vp
        self.darea = darea
        self.darea.show()

#        w = darea.get_root_window()
#        events = w.get_events()
#        print events
##        events |= Gdk.EventMask.ENTER_NOTIFY_MASK
#        events |= Gdk.EventMask.ALL_EVENTS_MASK
#        print events
#        w.set_events(events)

        img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        vp = Gtk.Viewport()
        vp.add(img)
        self.image = vp
        self.image.show()

        self.add(self.image)
        
        self.txt_tst_buf = ""

##     def on_darea_realize(self, widget):
##         print ("realize", widget)

##         w = self.darea.get_root_window()
##         events = w.get_events()
## #        print events
##         events |= Gdk.EventMask.ENTER_NOTIFY_MASK
## #        events |= Gdk.EventMask.ALL_EVENTS_MASK
## #        print events
##         w.set_events(events)
#        self.darea.connect('key-press-event', self.on_key_press_event)
#        self.darea.connect('enter-notify-event', self.on_enter_notify_event)
        self.darea.connect('focus-in-event', self.on_focus_in_event)
        self.darea.grab_focus()

    def subdoc_new(self, docid):
        self.textbuffers[docid] = EditorTextBuffer()

    def set_visible(self, docid):
        #print(">>> set_visible = " + str(docid))
        visid = self.textbuffer_visibleid
        if visid == -1 and docid is not None:
            assert(self.textbuffers[docid] is not None)
            self.remove(self.image)
            self.add(self.darea)
            self.textbuffer_visibleid = docid
        elif visid != -1 and docid is None:
            self.remove(self.darea)
            self.add(self.image)
            self.textbuffer_visibleid = -1

        if docid:
        #     self.textview.set_buffer(self.textbuffers[docid])
            self.textbuffer_visibleid = docid

    def subdoc_load_from_file(self, docid, filename):
        assert(self.textbuffers[docid] is not None)
        self.textbuffers[docid].load_from_file(filename)

    def subdoc_save_to_file(self, docid, filename):
        assert(self.textbuffers[docid] is not None)
        self.textbuffers[docid].save_to_file(filename)

    def subdoc_set_title(self, docid, title):
        self.textbuffers[docid].set_title(title)

    def subdoc_get_content_as_text(self, docid):
        assert(self.textbuffers[docid] is not None)
        return self.textbuffers[docid].get_content_as_text()

    def on_draw(self, widget, ctx):
        #print(ctx)
        # "ctx" is "cairo.Context" object

        layout = PangoCairo.create_layout(ctx)
        #pangoctx = layout.get_context()
        #ink_rect, logical_rect = layout.get_extents() # ret in Pango units
        #print(ink_rect.width, ink_rect.height, logical_rect.width, logical_rect.height)
        #ink_rect, logical_rect = layout.get_pixel_extents() # ret in pixels unit
        #print(ink_rect.width, ink_rect.height, logical_rect.width, logical_rect.height)

        # Following draw a gray background
        rect = widget.get_allocation() # return CairoRectangleInt
        #print(rect.x, rect.y, rect.width, rect.height)
        ctx.save()
        ctx.set_source_rgb(0.8, 0.8, 0.8)
        ctx.rectangle(rect.x, rect.y, rect.width, rect.height)
        ctx.fill()
        ctx.restore()

        # Draw a paragraph 'containers', with margin_x, margin_y
        ctx.translate(10, 20)
        para_width = rect.width - 10 * 2
        #print(para_width)

        ## helper to draw cursor with rectangle...
        #strong_rect, weak_rect = get_cursor_position(para_idx)

        desc = Pango.font_description_from_string("Times 20")
        layout.set_font_description(desc)
        layout.set_width(para_width * Pango.SCALE)
        layout.set_wrap(Pango.WrapMode.WORD_CHAR)
        layout.set_text(self.txt_tst_buf, -1)
        _w, _h = layout.get_size()
        textwidth  = _w / Pango.SCALE
        textheight = _h / Pango.SCALE

        # Fill the paragraph background in white
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0, 0, para_width, textheight)
        ctx.fill()

        # Draw a black line to delimit the paragraph position
        ctx.set_source_rgb(0, 0, 0)
        ctx.rectangle(0, 0, para_width, textheight)
        ctx.set_line_width(1)
        ctx.stroke()

        PangoCairo.update_layout(ctx, layout)
        PangoCairo.show_layout(ctx, layout)

    def on_enter_notify_event(self, widget, event):
        print("notify")
        widget.grab_focus()
        
    def on_focus_in_event(self, widget, event):
        print("focusin")
        widget.grab_focus()

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        # debug string :
        print(key + str(event.state))
        #print(event.keyval)
        entry = Gdk.keyval_to_unicode(event.keyval)
        print(entry)
        
        #if event.keyval in range(ord('a'), ord('z')):
        if entry >= 32:
            self.txt_tst_buf += unicode(event.string, encoding='utf-8')
        elif entry == 8: #backspace
            self.txt_tst_buf = self.txt_tst_buf[:-1]

        self.darea.queue_draw()

        return True

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

