#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import cairo
from gi.repository import Gdk, GObject, Gtk, Pango, PangoCairo
from lxml import etree

from editortextview import EditorTextView
from editortextbuffer import EditorTextBuffer

class SubdocView(Gtk.Container):
    __gtype_name__ = 'SubdocView'

    PARAGRAPH = 1
    IMAGE = 2

    def __init__(self):
        Gtk.Container.__init__(self)

        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)

        self.childrens = {} # list of block elements
        self.nb_blocks = 0
        self.focused_child = None

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
        mini = b
        natural = mini
        #print("")
        for docid, ch in self.childrens.items():
            child_mini, child_natural = ch.get_preferred_height()
            #print(ch, child_mini, child_natural)
            mini += child_mini + b
            natural += child_natural + b

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
            child_alloc.width, _dont_care_ = child.get_preferred_width()
            if child.get_property("hexpand") == True:
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
            if child == self.focused_child:
                ctx.set_line_width(4)
            else:
                ctx.set_line_width(1)
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
            self.subdoc_new()
            return True
        elif key =='BackSpace':
            if self.focused_child and self.focused_child.is_deletable():
                for key, widget in self.childrens.items():
                    if widget == self.focused_child:
                        if key > 0:
                            self.remove(widget)
                            self.focused_child = self.childrens[key-1]
                            self.focused_child.grab_focus()
                            self.queue_draw()
                        else:
                            self.remove(widget)
                            self.subdoc_new()

        retval = Gtk.Container.do_key_press_event(self, event)
        print ("   %s" % str(retval))
        return retval

    # Gtk.Container methods override
    def do_child_type(self):
        return Gtk.Widget # ProjectView ?

    def do_add(self, widget):
        widget.set_parent(self)
        idx = self.nb_blocks
        self.childrens[idx] = widget
        widget.grab_focus()
        self.focused_child = widget
        self.nb_blocks += 1

        if widget.get_visible():
            self.queue_resize()

    def do_remove(self, widget):
        for key, val in self.childrens.items():
            if val == widget:

                if widget == self.focused_child:
                    self.focused_child = None

                del self.childrens[key]

                # Shift all childs indexes
                if key < self.nb_blocks - 1:
                    for i in range(key, self.nb_blocks - 1):
                        self.childrens[i] = self.childrens[i+1]
                self.nb_blocks -= 1

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

    # Signals (mostly from childs)
    def on_child_focus_in(self, widget, event):
        #print(event)
        self.focused_child = widget
        self.queue_draw()

    # Application accessors
    def subdoc_new(self, subdoc_type = PARAGRAPH):
        #print("subdoc_new:")
        if subdoc_type == SubdocView.PARAGRAPH:
            buf = EditorTextBuffer()
            widget = EditorTextView()
            widget.set_buffer(buf)
            self.add(widget)
        elif subdoc_type == SubdocView.IMAGE:
            print("Image insertion asked")
        else:
            raise AttributeError

        widget.connect("focus-in-event", self.on_child_focus_in)

    def load_from_file(self, filename):

        # Remove previous widgets (should be done elsewhere !)
        while self.nb_blocks != 0:
            self.remove(self.childrens[self.nb_blocks-1])

        with open(filename, 'r') as f:
            data = f.read()
            data = data.decode('utf-8')

            # Parse XML file to add node recursively
            subdoc = etree.fromstring(data)
            assert(subdoc.tag == 'subdoc')

            para_list = subdoc.findall('p')
            for para in para_list:
                self.subdoc_new(subdoc_type = SubdocView.PARAGRAPH)
                sub = self.childrens[self.nb_blocks-1]
                assert (sub is not None)
                sub.set_content_from_html(para.text)

    def save_to_file(self, filename):
        subdoc = etree.Element('subdoc')
        tree = etree.ElementTree(subdoc)
        for docid, child in self.childrens.items():
            tag_name = child.get_serialize_tag_name()
            childnode = etree.SubElement(subdoc, tag_name)
            childnode.text = child.get_content_as_html()
        with open(filename, 'w') as f:
            tree.write(f, pretty_print=True)

    def get_content_as_text(self):
        assert(self.childrens[0] is not None)
        return self.childrens[0].get_content_as_text()

GObject.type_register(SubdocView)
