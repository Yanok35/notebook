#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import cairo
from gi.repository import Gdk, GObject, Gtk, Pango, PangoCairo

from editortextview import EditorTextView
from editortextbuffer import EditorTextBuffer

class SubdocView(Gtk.Container):
    __gtype_name__ = 'SubdocView'

    def __init__(self):
        Gtk.Container.__init__(self)

        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)

        self.childrens = {} # list of block elements
        self.set_has_window(False)
        self.set_border_width(10) # for debug only

    def do_get_request_mode(self):
        return(Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH)
        #return(Gtk.SizeRequestMode.CONSTANT_SIZE)

    # Gtk.Widget methods override
    def do_get_preferred_width(self):
        mini = 2 * self.get_border_width()
        natural = mini
        for docid, ch in self.childrens.items():
            child_mini, child_natural = ch.get_preferred_width()
            if child_mini > mini:
                mini = child_mini
            if child_natural > natural:
                natural = child_natural

        return (mini, natural)

    def do_get_preferred_height(self):
        b = self.get_border_width()
        mini = 2 * b
        natural = mini
        #print("")
        for docid, ch in self.childrens.items():
            child_mini, child_natural = ch.get_preferred_height()
            #print(ch, child_mini, child_natural)
            mini += child_mini + 2 * b
            natural += child_natural + 2 * b

        return (mini, natural)

    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)
        #print("parent [x,y,w,h]=", allocation.x,
        #    allocation.y, allocation.width, allocation.height)

        b = self.get_border_width()
        child_alloc = Gdk.Rectangle()
        child_alloc.x = allocation.x + b
        child_alloc.y = allocation.y + b
        for key, child in self.childrens.items():
            #child_alloc.width, _dont_care_ = child.get_preferred_width()
            if child_alloc.width < allocation.width - 2 * b:
                child_alloc.width = allocation.width - 2 * b
            child_alloc.height, _dont_care_ = child.get_preferred_height()
            child.size_allocate(child_alloc)
            #print("child %d [x,y,w,h]=" % docid,
            #    child_alloc.x, child_alloc.y, child_alloc.width, child_alloc.height)
            child_alloc.y += child_alloc.height + b

        # TODO: optimize changing area... (keep track of previous allocs)
        if self.get_window():
            Gdk.Window.invalidate_rect(self.get_window(), allocation, True)
            Gdk.Window.process_updates(self.get_window(), True)

    def do_draw(self, ctx):
        ctx.save()
        rect = self.get_allocation()
        ctx.translate(-rect.x, -rect.y) # to match Gtk absolute coord

        # Draw a background
        #ctx.set_source_rgb(1, 1, 1) # white
        ctx.set_source_rgb(0.9, 0.9, 0.9) # grey90
        ctx.paint()
        ctx.set_source_rgb(0, 0, 0) # black

        # ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
        #     cairo.FONT_WEIGHT_NORMAL)
        # ctx.set_font_size(12)
        # ctx.move_to(10, 20)
        # ctx.show_text("This is hello")

        # # Cross for layout debugging
        # ctx.set_line_width(1)
        # ctx.move_to(rect.x, rect.y)
        # ctx.line_to(rect.x + rect.width, rect.y + rect.height)
        # ctx.move_to(rect.x + rect.width, rect.y)
        # ctx.line_to(rect.x, rect.y + rect.height)
        # ctx.stroke()

        # Blue rectangle to outline childrends (debug also)
        #ctx.save()
        for docid, child in self.childrens.items():
            if not child.get_visible():
                continue
            rect = child.get_allocation()
            ctx.set_line_width(4)
            ctx.set_source_rgb(0, 0, 1) # blue
            ctx.rectangle(rect.x, rect.y, rect.width, rect.height)
            ctx.stroke()
            #print (rect.x, rect.y, rect.width, rect.height)
        #ctx.restore()

        ## Horizontal line to outline subdoc title
        #ctx.save()
        #for docid, child in self.childrens_title.items():
        #    if not child.get_visible():
        #        continue
        #    parent_rect = self.get_allocation()
        #    rect = child.get_allocation()
        #    ctx.set_line_width(2)
        #    ctx.set_source_rgb(0, 0, 0) # black
        #    ctx.move_to(rect.x, rect.y + rect.height)
        #    ctx.line_to(rect.x + parent_rect.width, rect.y + rect.height)
        #    ctx.stroke()
        #    #print (rect.x, rect.y, rect.width, rect.height)
        #ctx.restore()

        #ctx.set_source_rgb(0, 0, 0) # black
        #ctx.save()
        #ctx.move_to(10, 50)
        ##super(Gtk.Container, self).do_draw(self.image, ctx)
        ##self.image.do_draw(self.image.get_parent_window(), ctx)
        ##ctx.show_text("This is hello")
        #self.image.draw(ctx)
        #ctx.restore()

        #self.queue_draw()
        #ctx.show_text(self.txt_tst_buf)
        ctx.restore()

        Gtk.Container.do_draw(self, ctx)
        return False

    def do_key_press_event(self, event):
        #print("key_press_event in subdocview")
        key = Gdk.keyval_name(event.keyval)
        if key == 'Return':
            print("todo: check block items focused, catch cursor and split if needed")
            return True

        retval = Gtk.Container.do_key_press_event(self, event)
        print ("   %s" % str(retval))
        return retval

    # Gtk.Container methods override
    def do_child_type(self):
        return Gtk.Widget # ProjectView ?

    def do_add(self, widget):
        widget.set_parent(self)
        self.childrens[0] = widget

        if widget.get_visible():
            self.queue_resize()

    def do_remove(self, widget):
        for key, val in self.childrens.items():
            if val == widget:
                del self.childrens[key]

                if widget.get_visible():
                    self.queue_resize()

                return

    def do_forall(self, include_int, callback):
        try:
            for docid, widget in self.childrens.items():
                callback(widget)
                #if ch.eventbox:
                #    callback (ch.eventbox)
                #else:
                #    callback (ch.widget)
        except AttributeError:
            pass # print 'AttribError'

    # Application accessors
    def subdoc_new(self):
        print("subdoc_new:")
        buf = EditorTextBuffer()
        editor = EditorTextView()
        editor.set_buffer(buf)
        self.add(editor)

    def load_from_file(self, filename):
        assert(self.childrens[0] is not None)
        self.childrens[0].load_from_file(filename)

    def save_to_file(self, filename):
        assert(self.childrens[0] is not None)
        self.childrens[0].save_to_file(filename)

    def get_content_as_text(self):
        assert(self.childrens[0] is not None)
        return self.childrens[0].get_content_as_text()

GObject.type_register(SubdocView)
