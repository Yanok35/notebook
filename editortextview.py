#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#-*- coding: utf8 -*-

# Unicode support
from __future__ import unicode_literals

import cairo
from gi.repository import Gdk, GLib, Gtk, Pango, PangoCairo

from editortextbuffer import EditorTextBuffer

BLINK_MS = 250
SUBDOC_WIDTH_MARGIN_PX = 10

class EditorTextView(Gtk.ScrolledWindow):
    __gtype_name__ = 'EditorTextView'

    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)

        self.set_size_request(400, -1)

        self.set_hexpand(True)
        self.set_vexpand(True)

        self.textbuffers = {} #EditorTextBuffer()
        self.textbuffer_visibleid = -1 # -1 means an image is displayed

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        vp = Gtk.Viewport()
        darea = Gtk.DrawingArea()
        darea.set_size_request(400, 2048)
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

        self.paragraphs = [] # list of list : (PangoLayout, unicode)
        self.para_nb = 0
        self.para_cursor_idx = 0

        self.cursor_blink_state = False
        self.thr_blink = Gdk.threads_add_timeout(
            GLib.PRIORITY_DEFAULT_IDLE, BLINK_MS, self.on_blink_cb, self)

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
        #ims = cairo.ImageSurface(cairo.FORMAT_ARGB32, 390, 60)
        ims = cairo.PDFSurface("output.pdf", 390, 60)
        ctx = cairo.Context(ims)
        self.draw_on_cairo_surface(ctx, 0, 0, 390, 60)
        #ims.write_to_png("test.png")
        return self.textbuffers[docid].get_content_as_text()

    def paragraph_new(self):

        cr = self.darea.get_window().cairo_create()

        layout = PangoCairo.create_layout(cr)
        text = unicode(str(""), encoding='utf-8')
        cursor_ptr = 0
        self.paragraphs.append([layout, text, cursor_ptr])
        self.para_nb += 1
        #self.self.para_cursor_idx += 1

    def on_blink_cb(self, widget):
        #print("blink", self.cursor_blink_state)

        self.cursor_blink_state = not self.cursor_blink_state
        self.darea.queue_draw()

        self.thr_blink = Gdk.threads_add_timeout(
            GLib.PRIORITY_DEFAULT_IDLE, BLINK_MS, self.on_blink_cb, self)

    def on_draw(self, widget, ctx):

        # Cannot be empty ?
        if self.para_nb == 0:
            self.paragraph_new()

        rect = widget.get_allocation() # return cairo.RectangleInt
        self.draw_on_cairo_surface(ctx, rect.x, rect.y, rect.width, rect.height)

    def draw_on_cairo_surface(self, ctx, x, y, width, height):
        #print(ctx)
        # "ctx" is "cairo.Context" object

        #layout = PangoCairo.create_layout(ctx)

        # Following draw a gray background
        #print(rect.x, rect.y, rect.width, rect.height)
        ctx.save()
        ctx.set_source_rgb(0.8, 0.8, 0.8)
        ctx.rectangle(x, y, width, height)
        ctx.fill()
        ctx.restore()

        # Margins for whole paragraph list
        ctx.translate(SUBDOC_WIDTH_MARGIN_PX, 20)

        desc = Pango.font_description_from_string("Times 16")

        i = 0
        for layout, text, cursor_ptr in self.paragraphs:
            # Draw a paragraph 'containers', with margin_x, margin_y
            para_width = width - SUBDOC_WIDTH_MARGIN_PX * 2
            #print(para_width)

            #desc = Pango.font_description_from_string("Times 20")
            layout.set_font_description(desc)
            layout.set_width(para_width * Pango.SCALE)
            layout.set_wrap(Pango.WrapMode.WORD_CHAR)
            layout.set_justify(True)
            layout.set_text(text, -1)
            _w, _h = layout.get_size()
            textwidth  = _w / Pango.SCALE
            textheight = _h / Pango.SCALE

            # Fill the paragraph background in white
            ctx.set_source_rgb(0.9, 0.9, 0.9)
            ctx.rectangle(0, 0, para_width, textheight)
            ctx.fill()

            # Draw a black line to delimit the paragraph position
            if i == self.para_cursor_idx: # and self.cursor_blink_state:
                ctx.set_source_rgb(0, 0, 0)
                ctx.rectangle(0, 0, para_width, textheight)
                ctx.set_line_width(0.5)
                ctx.stroke()

            ## helper to draw cursor with rectangle...
            if i == self.para_cursor_idx and not self.cursor_blink_state:
                ctx.set_source_rgb(0, 0, 0)
                ctx.set_line_width(1)
                strong_rect, weak_rect = layout.get_cursor_pos(cursor_ptr)
                ctx.rectangle(strong_rect.x / Pango.SCALE,
                              strong_rect.y / Pango.SCALE,
                              strong_rect.width / Pango.SCALE,
                              strong_rect.height / Pango.SCALE)
                ctx.stroke()

            ctx.set_source_rgb(0, 0, 0)
            PangoCairo.update_layout(ctx, layout)
            PangoCairo.show_layout(ctx, layout)
            
            ctx.translate(0, 10 + textheight)
            i += 1

    def on_enter_notify_event(self, widget, event):
        print("notify")
        widget.grab_focus()
        
    def on_focus_in_event(self, widget, event):
        print("focusin")
        widget.grab_focus()

    def on_key_press_event(self, window, event):
        key = Gdk.keyval_name(event.keyval)

        # debug string :
        entry = Gdk.keyval_to_unicode(event.keyval)
        print(key + "|" + str(event.state) + "|" + str(entry))
        #print(event.keyval)
        #print(entry)

        #self.paragraphs[self.para_cursor_idx]
        #if event.keyval in range(ord('a'), ord('z')):
        if entry >= 32:
            text = unicode(event.string, encoding='utf-8')
            self.paragraphs[self.para_cursor_idx][1] += text
            text = text.encode('utf_8')
            self.paragraphs[self.para_cursor_idx][2] += len(text)
        elif entry == 8: #backspace
            if len(self.paragraphs[self.para_cursor_idx][1]):
                text = (self.paragraphs[self.para_cursor_idx][1])[-1:]
                text = text.encode('utf_8')
                self.paragraphs[self.para_cursor_idx][2] -= len(text)
                self.paragraphs[self.para_cursor_idx][1] = (self.paragraphs[self.para_cursor_idx][1])[:-1]
            elif self.para_cursor_idx:
                del self.paragraphs[self.para_cursor_idx]
                self.para_cursor_idx -= 1
                self.para_nb -= 1
        elif entry == 13: # carriage return
            self.paragraph_new()
            self.para_cursor_idx += 1

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

