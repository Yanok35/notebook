#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import cairo
from gi.repository import Gdk, GObject, Gtk, PangoCairo

#from editortextbuffer import EditorTextBuffer

class ProjectView(Gtk.Container):
    __gtype_name__ = 'ProjectView'

    def __init__(self):
        Gtk.Container.__init__(self)

        self.childrens = []

        #self.set_has_window(True) # implie do_realize presence
        self.set_has_window(False)
        self.set_size_request(600, -1)
        #self.set_hexpand(True)
        #self.set_vexpand(True)

        img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        vp = Gtk.Viewport()
        vp.add(img)
        self.image = vp
        self.add(self.image)

    def do_get_request_mode(self):
        return(Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH)
        #return(Gtk.SizeRequestMode.CONSTANT_SIZE)

    # Gtk.Widget methods override
    def do_get_preferred_width(self):
        mini = self.get_border_width()
        sum = 0
        for ch in self.childrens:
            _x_, req = ch.get_preferred_width()
            sum += req
        return (mini, sum)

    def do_get_preferred_height(self):
        mini = self.get_border_width()
        sum = 0
        for ch in self.childrens:
            _x_, req = ch.get_preferred_height()
            sum += req
        return (mini, sum)

    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)
        b = self.get_border_width()

        child_alloc = Gdk.Rectangle()

        nb = len(self.childrens)
        #child_alloc.x = allocation.x + b #+ 10
        #child_alloc.y = allocation.y + b #+ 40

        i = 0
        for child in self.childrens:
            child_alloc.x = allocation.x + b #+ 10
            child_alloc.y = allocation.y + b + ((allocation.height - b) / nb) * i
            b <<= 1
            child_alloc.width  = allocation.width  - b #- 100
            child_alloc.height = (allocation.height - b) / nb #- 40

            mini, _dont_care_ = child.get_preferred_height()
            if _dont_care_ < child_alloc.height:
                child_alloc.height = _dont_care_

            child.size_allocate(child_alloc)
            print("child%d at :" % i, 
                child_alloc.x, child_alloc.y, child_alloc.width, child_alloc.height)
            i += 1

    #def do_realize(self):
    #    print "do_realize"

    #    allocation = self.get_allocation()
    #    attr = Gdk.WindowAttr()
    #    attr.window_type = Gdk.WindowType.CHILD
    #    attr.x = allocation.x
    #    attr.y = allocation.y
    #    attr.width = allocation.width
    #    attr.height = allocation.height
    #    attr.visual = self.get_visual()
    #    attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
    #    WAT = Gdk.WindowAttributesType
    #    mask = WAT.X | WAT.Y | WAT.VISUAL
    #    window = Gdk.Window(self.get_parent_window(), attr, mask);
    #    self.set_window(window)
    #    self.register_window(window)
    #    self.set_realized(True)
    #    #self.set_visible(True)
    #    print window

    #    #window.invalidate_rect(allocation, True)
    #    #window.process_updates(True)
    #    self.add(self.image)

    def do_draw(self, ctx):
        # Draw a white background
        ctx.set_source_rgb(1, 1, 1) # white
        ctx.paint()

        ctx.set_source_rgb(0, 0, 0) # black
        ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
            cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(12)
        ctx.move_to(10, 20)
        ctx.show_text("This is hello")

        rect = self.get_allocation()
        ctx.set_line_width(1)
        ctx.move_to(rect.x, rect.y)
        ctx.line_to(rect.x + rect.width, rect.y + rect.height)
        ctx.move_to(rect.x + rect.width, rect.y)
        ctx.line_to(rect.x, rect.y + rect.height)
        ctx.stroke()

        #ctx.save()
        #ctx.move_to(10, 50)
        ##super(Gtk.Container, self).do_draw(self.image, ctx)
        ##self.image.do_draw(self.image.get_parent_window(), ctx)
        ##ctx.show_text("This is hello")
        #self.image.draw(ctx)
        #ctx.restore()

        #self.queue_draw()
        #ctx.show_text(self.txt_tst_buf)
        Gtk.Container.do_draw(self, ctx)
        return False

    # Gtk.Container methods override
    def do_child_type(self):
        return Gtk.Widget # ProjectView ?

    def do_add(self, widget):
        print('do_add', len(self.childrens))
        widget.set_parent(self)
        self.childrens.append(widget)
        
        if widget.get_visible():
            self.queue_resize()

    def do_remove(self, widget):
        if widget in self.childrens:
            self.childrens.remove(widget)

            if widget.get_visible():
                self.queue_resize()

    def do_forall(self, include_int, callback):
        try:
            for ch in self.childrens:
                callback(ch)
                #if ch.eventbox:
                #    callback (ch.eventbox)
                #else:
                #    callback (ch.widget)
        except AttributeError:
            pass # print 'AttribError'

    # Application accessors
    def subdoc_new(self, docid):
        pass #self.textbuffers[docid] = EditorTextBuffer()

    #def set_visible(self, docid):
    #    #print(">>> set_visible = " + str(docid))
    #    visid = self.textbuffer_visibleid
    #    if visid == -1 and docid is not None:
    #        assert(self.textbuffers[docid] is not None)
    #        self.remove(self.image)
    #        #self.add(self.textview)
    #        self.textbuffer_visibleid = docid
    #    elif visid != -1 and docid is None:
    #        #self.remove(self.textview)
    #        self.add(self.image)
    #        self.textbuffer_visibleid = -1

    #    if docid:
    #        #self.textview.set_buffer(self.textbuffers[docid])
    #        self.textbuffer_visibleid = docid

    def subdoc_load_from_file(self, docid, filename):
        assert(self.textbuffers[docid] is not None)
        #self.textbuffers[docid].load_from_file(filename)

    def subdoc_save_to_file(self, docid, filename):
        assert(self.textbuffers[docid] is not None)
        #self.textbuffers[docid].save_to_file(filename)

    def subdoc_set_title(self, docid, title):
        #self.textbuffers[docid].set_title(title)
        pass

    def subdoc_get_content_as_text(self, docid):
        assert(self.textbuffers[docid] is not None)
        #return self.textbuffers[docid].get_content_as_text()

GObject.type_register(ProjectView)
