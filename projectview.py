#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import cairo
from gi.repository import Gdk, GObject, Gtk, Pango, PangoCairo

from editortextview import EditorTextView
from editortextbuffer import EditorTextBuffer

class ProjectView(Gtk.Container):
    __gtype_name__ = 'ProjectView'

    def __init__(self):
        Gtk.Container.__init__(self)

        self.childrens = {}
        self.childrens_title = {}
        self.visible_docid_list = []

        #self.set_has_window(True) # implie do_realize presence
        self.set_has_window(False)
        #self.set_size_request(100, -1)
        #self.set_hexpand(True)
        #self.set_vexpand(True)

        img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        vp = Gtk.Viewport()
        vp.add(img)
        self.image = vp
        #self.add(self.image)
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

        # FIXME : parse title_widget to check also their lengths
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

        for docid, ch in self.childrens_title.items():
            child_mini, child_natural = ch.get_preferred_height()
            mini += child_mini
            natural += child_natural
        return (mini, natural)

    def do_size_allocate(self, allocation):
        self.set_allocation(allocation)
        #print("parent [x,y,w,h]=", allocation.x,
        #    allocation.y, allocation.width, allocation.height)

        b = self.get_border_width()
        child_alloc = Gdk.Rectangle()
        child_alloc.x = allocation.x + b
        child_alloc.y = allocation.y + b
        for docid in self.visible_docid_list:
            child_label = self.childrens_title[docid]
            child_alloc.width, _dont_care_ = child_label.get_preferred_width()
            #if child_alloc.width < allocation.width - 2 * b:
            #    child_alloc.width = allocation.width - 2 * b
            child_alloc.height, _dont_care_ = child_label.get_preferred_height()
            child_label.size_allocate(child_alloc)
            #print("child_label %d [x,y,w,h]=" % docid,
            #    child_alloc.x, child_alloc.y, child_alloc.width, child_alloc.height)
            child_alloc.y += child_alloc.height + b

            child = self.childrens[docid]
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
    #    #window.invalidate_rect(allocation, True)

        #child_alloc = Gdk.Rectangle()
        #nb = len(self.childrens)
        #i = 0
        #for child in self.childrens:
        #    b = self.get_border_width()
        #    child_alloc.x = allocation.x + b #+ 10
        #    child_alloc.y = allocation.y + b + ((allocation.height - b) / nb) * i
        #    #b <<= 1
        #    b *= 2
        #    child_alloc.width  = allocation.width  - b #- 100
        #    child_alloc.height = (allocation.height - b) / nb #- 40

        #    # mini, _dont_care_ = child.get_preferred_height()
        #    # if mini > child_alloc.height:
        #    #     child_alloc.height = mini

        #    child.size_allocate(child_alloc)
        #    #print("child %d [x,y,w,h]=" % i,
        #    #    child_alloc.x, child_alloc.y, child_alloc.width, child_alloc.height)
        #    i += 1

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
        ctx.save()
        rect = self.get_allocation()
        ctx.translate(-rect.x, -rect.y)

        # Draw a white background
        ctx.set_source_rgb(1, 1, 1) # white
        ctx.paint()
        ctx.set_source_rgb(0, 0, 0) # black

        # ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
        #     cairo.FONT_WEIGHT_NORMAL)
        # ctx.set_font_size(12)
        # ctx.move_to(10, 20)
        # ctx.show_text("This is hello")

        # # Cross for layout debugging
        # rect = self.get_allocation()
        # ctx.set_line_width(1)
        # ctx.move_to(rect.x, rect.y)
        # ctx.line_to(rect.x + rect.width, rect.y + rect.height)
        # ctx.move_to(rect.x + rect.width, rect.y)
        # ctx.line_to(rect.x, rect.y + rect.height)
        # ctx.stroke()

        # Red rectangle to outline childrends (debug also)
        ctx.save()
        for docid, child in self.childrens.items():
            if not child.get_visible():
                continue
            rect = child.get_allocation()
            ctx.set_line_width(4)
            ctx.set_source_rgb(1, 0, 0) # red
            ctx.rectangle(rect.x, rect.y, rect.width, rect.height)
            ctx.stroke()
            #print (rect.x, rect.y, rect.width, rect.height)
        ctx.restore()

        # Horizontal line to outline subdoc title
        ctx.save()
        for docid, child in self.childrens_title.items():
            if not child.get_visible():
                continue
            parent_rect = self.get_allocation()
            rect = child.get_allocation()
            ctx.set_line_width(2)
            ctx.set_source_rgb(0, 0, 0) # black
            ctx.move_to(rect.x, rect.y + rect.height)
            ctx.line_to(rect.x + parent_rect.width, rect.y + rect.height)
            ctx.stroke()
            #print (rect.x, rect.y, rect.width, rect.height)
        ctx.restore()

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

    # Gtk.Container methods override
    def do_child_type(self):
        return Gtk.Widget # ProjectView ?

    def do_add(self, widget):
        try:
            docid = widget.__getattribute__('docid')
        except AttributeError:
            print ("invalid API. use subdoc_new() to pack something")
            return
            #docid = 0

        widget.set_parent(self)
        if (str(type(widget)) != "<class 'editortextview.EditorTextView'>"):
            print('do_add', docid, widget)
            self.childrens_title[docid] = widget
        else:
            self.childrens[docid] = widget
        
        if widget.get_visible():
            self.queue_resize()

    def do_remove(self, widget):
        for key, val in self.childrens.items():
            if val == widget:
                del self.childrens[key]
                del self.childrens_title[key]

                if widget.get_visible():
                    self.queue_resize()

                return

    def do_forall(self, include_int, callback):
        try:
            for docid, widget in self.childrens.items():
                callback(widget)

            for docid, widget in self.childrens_title.items():
                callback(widget)
                #if ch.eventbox:
                #    callback (ch.eventbox)
                #else:
                #    callback (ch.widget)
        except AttributeError:
            pass # print 'AttribError'

    # Application accessors
    def subdoc_new(self, docid):
        print("subdoc_new:", docid)
        buf = EditorTextBuffer()
        editor = EditorTextView()
        editor.set_buffer(buf)
        editor.__setattr__("docid", docid)
        self.add(editor)

        label_widget = Gtk.Label()
        #label_widget.set_size_request(100, 100)
        fontdesc = Pango.FontDescription("Serif Bold 15")
        label_widget.modify_font(fontdesc)
        label_widget.set_justify(Gtk.Justification.LEFT)
        #label_widget.set_visible(True)
        label_widget.__setattr__("docid", docid)
        self.add(label_widget)

    def subdoc_set_visible(self, docid_list):
        # print(">>> set_visible = " + str(docid_list))
        for docid, widget in self.childrens.items():
            if docid in docid_list:
                self.childrens_title[docid].set_visible(True)
                #self.childrens_title[docid].show()
                widget.set_visible(True)
            else:
                self.childrens_title[docid].set_visible(False)
                #self.childrens_title[docid].hide()
                widget.set_visible(False)
        self.visible_docid_list = docid_list
        pass
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
        assert(self.childrens[docid] is not None)
        self.childrens[docid].load_from_file(filename)

    def subdoc_save_to_file(self, docid, filename):
        assert(self.childrens[docid] is not None)
        self.childrens[docid].save_to_file(filename)

    def subdoc_set_title(self, docid, title):
        assert(self.childrens_title[docid] is not None)
        #self.childrens_title[docid].set_text(title) # FIXME: use set markup...
        self.childrens_title[docid].set_label(title) # FIXME: use set markup...
        self.queue_draw()
        #self.childrens[docid].set_title(title)

    def subdoc_get_content_as_text(self, docid):
        assert(self.childrens[docid] is not None)
        return self.childrens[docid].get_content_as_text()

GObject.type_register(ProjectView)
