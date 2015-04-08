#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import copy

from gi.repository import Gdk, GdkPixbuf, GObject, Gtk, GtkSource, Pango

from ielementblock import ElementBlockInterface

class ImageView(Gtk.Layout, ElementBlockInterface):
    __gtype_name__ = 'ImageView'

    __gsignals__ = copy.copy(ElementBlockInterface.__gsignals__)

    def __init__(self, **args):
        Gtk.Layout.__init__(self, **args)

        self.set_size_request(600, 50)
        self.set_hexpand(False)
        #self.set_double_buffered(False)
        #self.set_has_window(True)
        #self.set_has_window(False)
        self.set_border_width(10) # for debug only
        self.button1_active = False
        #self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        #self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)

        #self.set_property('can-focus', True)

        self.childwidget = None
        self.child_newx = 0
        self.child_newy = 0

        #img = Gtk.Image.new_from_file("oshw-logo-800-px.png")
        #img.connect('button-press-event', self.do_button_press_event)

        #self.set_events(0)
        #self.add_events(Gdk.EventMask.EXPOSURE_MASK)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.add_events(Gdk.EventMask.BUTTON_RELEASE_MASK)
        self.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
        #self.add_events(Gdk.EventMask.BUTTON_MOTION_MASK)
        #self.add_events(Gdk.EventMask.KEY_PRESS_MASK)
        #print("init: get_events = ", self.get_events())

        self.set_can_default(True)
        self.set_can_focus(True)

        #img.set_property('can-focus', True)
        #vp = Gtk.Viewport()
        #vp.set_size_request(50, 50)
        #vp.add(img)
        #vp.show()
        #self.add(vp)

        #self.add(img)
        self.show_all()

#    def do_get_request_mode(self):
#        #return(Gtk.SizeRequestMode.HEIGHT_FOR_WIDTH)
#        return(Gtk.SizeRequestMode.CONSTANT_SIZE)

    # Gtk.Widget methods override

    #def do_ajust_size_request(self, orientation, minimum_size, natural_size):
    #    print("do_ajust_size_request")
    #    return Gtk.Widget.do_adjust_size_allocation(self, orientation, minimum_size, natural_size)

#    def do_adjust_size_allocation(self,
#            orientation, minimum_size, natural_size, allocated_pos, allocated_size):
#        print("do_adjust_size_allocation")
#        print(orientation, minimum_size, natural_size, allocated_pos, allocated_size)
##        return super(ImageView, self).do_adjust_size_allocation(self,
##            orientation, minimum_size, natural_size, allocated_pos, allocated_size)
##        return Gtk.Container.do_adjust_size_allocation(self,
##            orientation, minimum_size, natural_size, allocated_pos, allocated_size)
#        pass

#    def do_get_preferred_width(self):
#        #print("do_get_preferred_width")
#        mini = 2 * self.get_border_width()
#        natural = mini
#        for docid, ch in self.childrens.items():
#            child_mini, child_natural = ch.get_preferred_width()
#            if child_mini > mini:
#                mini = child_mini
#            if child_natural > natural:
#                natural = child_natural
#
#        return (mini, natural)
#
#    def do_get_preferred_height(self):
#        #print("do_get_preferred_height")
#        b = self.get_border_width()
#        mini = b
#        natural = mini
#        #print("")
#        for docid, ch in self.childrens.items():
#            child_mini, child_natural = ch.get_preferred_height()
#            #print(ch, child_mini, child_natural)
#            mini += child_mini + b
#            natural += child_natural + b
#
#        return (mini, natural)
#
##    def do_get_preferred_height_for_width(self, width):
##        print('do_get_preferred_height_for_width')
##        return self.do_get_preferred_height()
##
##    def do_get_preferred_width_for_height(self, height):
##        print('do_get_preferred_width_for_height')
##        return self.do_get_preferred_width()
#
#    #def do_get_preferred_height_and_baseline_for_width(self, width):
#    #    print('do_get_preferred_height_and_baseline_for_width')
#    #    return self.do_get_preferred_height()
#
#    def do_size_allocate(self, allocation):
#        #print('do_size_allocate')
#        self.set_allocation(allocation)
#        #print("parent [x,y,w,h]=", allocation.x,
#        #    allocation.y, allocation.width, allocation.height)
#
#        b = self.get_border_width()
#        child_alloc = Gdk.Rectangle()
#        child_alloc.x = allocation.x + b
#        child_alloc.y = allocation.y + b
#        for key, child in self.childrens.items():
#            #child_alloc.width, _dont_care_ = child.get_preferred_width()
#            if child_alloc.width < allocation.width - 2 * b:
#                child_alloc.width = allocation.width - 2 * b
#            child_alloc.height, _dont_care_ = child.get_preferred_height()
#            child.size_allocate(child_alloc)
#            #print("child %d [x,y,w,h]=" % docid,
#            #    child_alloc.x, child_alloc.y, child_alloc.width, child_alloc.height)
#            child_alloc.y += child_alloc.height + b
#
#        if self.get_realized():
#            Gdk.Window.move_resize(self.window,
#                allocation.x, allocation.y, allocation.width, allocation.height)
#            #Gdk.Window.resize
#
#            #Gdk.Window.invalidate_rect(self.get_window(), allocation, True)
#            #Gdk.Window.process_updates(self.get_window(), True)

    def do_draw(self, ctx):
        #print('do_draw')
        ctx.save()
        rect = self.get_allocation()
        ctx.translate(-rect.x, -rect.y) # to match Gtk absolute coord

        # Draw a background
        #ctx.set_source_rgb(1, 1, 1) # white
        ##ctx.set_source_rgb(0.5, 0.5, 0.5) # grey50
        #ctx.paint()
        #ctx.set_source_rgb(0, 0, 0) # black

        # ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL,
        #     cairo.FONT_WEIGHT_NORMAL)
        # ctx.set_font_size(12)
        # ctx.move_to(10, 20)
        # ctx.show_text("This is hello")

        # Cross for layout debugging
        #ctx.save()
        if not self.childwidget:
            ctx.set_line_width(1)
            ctx.move_to(rect.x, rect.y)
            ctx.line_to(rect.x + rect.width, rect.y + rect.height)
            ctx.move_to(rect.x + rect.width, rect.y)
            ctx.line_to(rect.x, rect.y + rect.height)
            ctx.stroke()
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
        Gtk.Layout.do_draw(self, ctx)

        # #ctx = Gdk.cairo_create(self.get_bin_window())
        # ctx.save()
        # # Cross for layout debugging
        # rect = self.get_allocation()
        # ctx.translate(-rect.x, -rect.y) # to match Gtk absolute coord
        # ctx.set_line_width(1)
        # ctx.move_to(rect.x, rect.y)
        # ctx.line_to(rect.x + rect.width/2, rect.y + rect.height)
        # ctx.move_to(rect.x + rect.width/2, rect.y)
        # ctx.line_to(rect.x, rect.y + rect.height)
        # ctx.stroke()

        #Gdk.Window.invalidate_rect(self.get_window(), rect, True)

        # self.queue_draw()
        # #Gdk.Window.invalidate_rect(self.get_bin_window(), rect, True)
        # #Gdk.Window.process_updates(self.get_bin_window(), True)

        # ctx.restore()

        return True

    #def do_map(self):
    #    print "do map"
    #    self.set_mapped(True)
    #    Gdk.Window.show(self.window)
    #    #Gdk.
    #    pass

#    def do_realize(self):
#        #print "do_realize"
#
#        self.set_realized(True)
#
#        allocation = self.get_allocation()
#        #print(allocation.x, allocation.y, allocation.width, allocation.height)
#        attr = Gdk.WindowAttr()
#        attr.window_type = Gdk.WindowType.CHILD
#        attr.wclass = Gdk.WindowWindowClass.INPUT_OUTPUT
#        attr.x = allocation.x
#        attr.y = allocation.y
#        attr.width = allocation.width
#        attr.height = allocation.height
#        attr.visual = self.get_visual()
#        attr.event_mask = self.get_events() | Gdk.EventMask.EXPOSURE_MASK
#        attr.event_mask |= Gdk.EventMask.BUTTON_PRESS_MASK
#        attr.event_mask |= Gdk.EventMask.BUTTON_RELEASE_MASK
#        attr.event_mask |= Gdk.EventMask.POINTER_MOTION_MASK
#        # pointer event only when clicked.
#        #attr.event_mask |= Gdk.EventMask.BUTTON1_MOTION_MASK
#
#        WAT = Gdk.WindowAttributesType
#        mask = WAT.X | WAT.Y | WAT.VISUAL
#        self.window = Gdk.Window(self.get_parent_window(), attr, mask);
#        self.set_window(self.window)
#        self.register_window(self.window)
#
#        self.set_has_window(True)

    def do_button_press_event(self, event):
        #print(str(event.type))
        #print("[x, y] = ", event.x, event.y)
        if event.type == Gdk.EventType.BUTTON_PRESS:
            print("button_press:")
            self.button1_startx = event.x #self.childwidget.get_property('x')
            self.button1_starty = event.y #self.childwidget.get_property('y')
            self.button1_active = True
            self.button1_action, _bis_, self.button1_dir = self._get_action_from_pointer_pos(event)

            print("\taction =", self.button1_action)
            
            self.grab_focus()
        elif event.type == Gdk.EventType._2BUTTON_PRESS:
            print("double click")
        
        return True

    def do_button_release_event(self, event):
        if event.type == Gdk.EventType.BUTTON_RELEASE:
            print("button_release:")
            if self.button1_action == 'move':
                self.childwidget_posx = self.child_newx
                self.childwidget_posy = self.child_newy
            self.button1_active = False

    def _get_action_from_pointer_pos(self, event):
        '''
        return a (str, cursor) tuple : ('crop', 'resize' or 'move', gdk cursor)
        '''
        rect = self.get_allocation()
        direction = None
        # FIXME: be sure 10pix is always possible.
        if event.x < 10 and event.y > 10 and event.y < rect.height - 10:
            #print('left handle for crop')
            cursor = Gdk.Cursor(Gdk.CursorType.LEFT_TEE)
            action = 'crop'
            direction = 'wl' # width, left

        elif event.x > rect.width - 10 and event.y > 10 and event.y < rect.height - 10:
            #print('right handle for crop')
            cursor = Gdk.Cursor(Gdk.CursorType.RIGHT_TEE)
            action = 'crop'
            direction = 'wr' # witdh, right

        elif event.y < 10 and event.x > 10 and event.x < rect.width - 10:
            #print('top handle for crop')
            cursor = Gdk.Cursor(Gdk.CursorType.TOP_TEE)
            action = 'crop'
            direction = 'ht' # height, top

        elif event.y > rect.height - 10 and event.x > 10 and event.x < rect.width - 10:
            #print('bottom handle for crop')
            cursor = Gdk.Cursor(Gdk.CursorType.BOTTOM_TEE)
            action = 'crop'
            direction = 'hb' # height, bottom

        elif event.x < 10 and event.y < 10:
            #print('corner for resize')
            cursor = Gdk.Cursor(Gdk.CursorType.TOP_LEFT_CORNER)
            action = 'resize'

        elif event.x > rect.width - 10 and event.y < 10:
            #print('corner for resize')
            cursor = Gdk.Cursor(Gdk.CursorType.TOP_RIGHT_CORNER)
            action = 'resize'

        elif event.x < 10 and event.y > rect.height - 10:
            #print('corner for resize')
            cursor = Gdk.Cursor(Gdk.CursorType.BOTTOM_LEFT_CORNER)
            action = 'resize'

        elif event.x > rect.width - 10 and event.y > rect.height - 10:
            #print('corner for resize')
            cursor = Gdk.Cursor(Gdk.CursorType.BOTTOM_RIGHT_CORNER)
            action = 'resize'

        else:
            cursor = Gdk.Cursor(Gdk.CursorType.ARROW)
            action = 'move'

        return (action, cursor, direction)

    def do_motion_notify_event(self, event):

        action, cursor, direction = self._get_action_from_pointer_pos(event)

        if self.button1_active:
            if self.button1_action == 'move':
                #print("motion but1 notify [%d,%d]" % (event.x, event.y))
                self.child_newx = self.childwidget_posx + (event.x - self.button1_startx)
                self.child_newy = self.childwidget_posy + (event.y - self.button1_starty)

                self.move(self.childwidget,
                    self.child_newx,
                    self.child_newy)
            elif self.button1_action == 'resize':
                dX = int(event.x - self.button1_startx)
                dY = int(event.y - self.button1_starty)
                #print("resize, [dX, dY] = ", dX, dY)
                
                rect = self.get_allocation()

                pixbuf = self.img.get_pixbuf()
                new_pixbuf = pixbuf.scale_simple(
                    rect.width + dX, rect.height + dY, GdkPixbuf.InterpType.BILINEAR)
                new_img = Gtk.Image.new_from_pixbuf(new_pixbuf)
                new_img.show()
                self.remove(self.childwidget)
                self.add(new_img)
                self.img = new_img
                self.childwidget = new_img
                #del pixbuf

                self.set_size_request(rect.width + dX, rect.height + dY)

                self.button1_startx = event.x
                self.button1_starty = event.y

            elif self.button1_action == 'crop':
                rect = self.get_allocation()
                dX = int(event.x - self.button1_startx)
                dY = int(event.y - self.button1_starty)
                #print("crop, [dX, dY] = ", dX, dY)

                # w, _dont_care_ = self.img.get_preferred_width()
                # h, _dont_care_ = self.img.get_preferred_height()

                # # prevent crop not to be an expand:
                # if   (self.button1_dir == 'wl' and rect.width - dX > w) \
                #   or (self.button1_dir == 'wr' and rect.width + dX > w) \
                #   or (self.button1_dir == 'ht' and rect.height - dY > h) \
                #   or (self.button1_dir == 'hb' and rect.height + dY > h):
                #     return

                # on top and left crop, we need to move the child in layout
                if self.button1_dir == 'wl':
                    self.childwidget_posx -= dX
                    self.move(self.childwidget,
                        self.childwidget_posx, self.childwidget_posy)

                elif self.button1_dir == 'ht':
                    self.childwidget_posy -= dY
                    self.move(self.childwidget,
                        self.childwidget_posx, self.childwidget_posy)

                # Do the crop
                if self.button1_dir == 'wl':
                    # width crop
                    self.set_size_request(rect.width - dX, rect.height)
                    self.button1_startx = event.x

                elif self.button1_dir == 'wr':
                    self.set_size_request(rect.width + dX, rect.height)
                    self.button1_startx = event.x

                elif self.button1_dir == 'ht':
                    # height crop
                    self.set_size_request(rect.width, rect.height - dY)
                    self.button1_starty = event.y

                elif self.button1_dir == 'hb':
                    self.set_size_request(rect.width, rect.height + dY)
                    self.button1_starty = event.y

        else:
            # button1 inactive...
            pass
            #rect = self.get_allocation()
            
            #if event.x < 10 and event.y > 10 and event.y < rect.height - 10:
            #    #print('left handle for crop')

            #    rect = self.get_allocation()
            #    #Gdk.Window.process_all_updates()#self.get_window(), True)

            #    #ctx = Gdk.cairo_create(self.get_bin_window())
            #    ctx = Gdk.cairo_create(self.get_window())
            #    Gdk.Window.invalidate_rect(self.get_window(), rect, True)
            #    Gdk.Window.process_all_updates()#self.get_window(), True)

            #    ctx.save()
            #    # Cross for layout debugging
            #    Gdk.Window.invalidate_rect(self.get_window(), rect, True)
            #    ctx.translate(-rect.x, -rect.y) # to match Gtk absolute coord
            #    ctx.set_line_width(1)
            #    ctx.move_to(rect.x, rect.y)
            #    ctx.line_to(rect.x + rect.width/2, rect.y + rect.height)
            #    ctx.move_to(rect.x + rect.width/2, rect.y)
            #    ctx.line_to(rect.x, rect.y + rect.height)
            #    ctx.stroke()

        gdk_window = self.get_window()
        gdk_window.set_cursor(cursor)

    def do_key_press_event(self, event):
        key = Gdk.keyval_name(event.keyval)
        # debug string :
        print("keypress: get_events = ", self.get_events())
        print(event.keyval)
        print(key + str(event.state), event.state)

        if key =='BackSpace':
            # let the subview handle the destruction...
            return False

        return True

    #    # Catch iter of the current cursor position
    #    buf = self.get_buffer()
    #    mark = buf.get_mark('insert')
    #    cur_iter = buf.get_iter_at_mark(mark)
    #    start_iter = buf.get_start_iter()
    #    end_iter = buf.get_end_iter()

    #    # Do not treat "Return" key normally... event is
    #    # up to subdocview container for block container addition
    #    if key == 'Return':
    #        if (event.state & Gdk.ModifierType.CONTROL_MASK) \
    #            or (event.state & Gdk.ModifierType.SHIFT_MASK) \
    #            or (event.state & Gdk.ModifierType.MOD1_MASK):
    #                pass
    #        else:
    #            print('Return key-press-event is up to subdoc view...')
    #            return False
    #    elif key =='BackSpace' \
    #        and not buf.get_property('has-selection') \
    #        and cur_iter.compare(start_iter) == 0:
    #            print("Backspace! delete itself (if empty) and change block - 1, last_pos")
    #            print("or merge with block - 1, if previous is text")
    #            return False
    #    elif key in ('Up', 'Down', 'Left', 'Right'):
    #        #print("cur_iter (av move!) l %d : c %d" % (cur_iter.get_line(), cur_iter.get_line_index()))
    #        #print("  visible: l %d : c %d" % (cur_iter.get_line(), cur_iter.get_visible_line_index()))

    #        if key == 'Left' and cur_iter.compare(start_iter) == 0:
    #            print("start of buf : should change block - 1, last_pos")
    #        elif key == 'Right' and cur_iter.compare(end_iter) == 0:
    #            print("end of buf : should change block + 1, first_pos")
    #        elif key == 'Up':
    #            next_line = cur_iter.copy()
    #            possible = self.backward_display_line(next_line)
    #            if not possible:
    #                print("first line : should change block - 1, pos %d" % cur_iter.get_line_offset())
    #                return True
    #        elif key == 'Down':
    #            next_line = cur_iter.copy()
    #            possible = self.forward_display_line(next_line)
    #            if not possible:
    #                print("last line : should change block + 1, pos %d" % cur_iter.get_line_offset())
    #                return True
    #    else:
    #        pass #print(key)

    #    ## #print("key_press_event in editortextview")
    #    retval = GtkSource.View.do_key_press_event(self, event)
    #    #print ("   %s" % str(retval))
    #    return retval

    # Gtk.Container methods override
#    def do_child_type(self):
#        return Gtk.Widget # ProjectView ?
#
#    def do_add(self, widget):
#        idx = self.nb_blocks
#        self.childrens[idx] = widget
#        widget.grab_focus()
#        self.focused_child = widget
#        self.nb_blocks += 1
#
#        widget.set_parent(self)
#        if self.get_realized():
#            widget.set_parent_window(self.get_window())
#        if widget.get_visible():
#            self.queue_resize()
#
#    def do_remove(self, widget):
#        for key, val in self.childrens.items():
#            if val == widget:
#
#                if widget == self.focused_child:
#                    self.focused_child = None
#
#                del self.childrens[key]
#
#                # Shift all childs indexes
#                if key < self.nb_blocks - 1:
#                    for i in range(key, self.nb_blocks - 1):
#                        self.childrens[i] = self.childrens[i+1]
#                self.nb_blocks -= 1
#
#                if widget.get_visible():
#                    self.queue_resize()
#
#                return
#
#    def do_forall(self, include_int, callback):
#        try:
#            for docid, widget in self.childrens.items():
#                callback(widget)
#                #if ch.eventbox:
#                #    callback (ch.eventbox)
#                #else:
#                #    callback (ch.widget)
#        except AttributeError:
#            pass # print 'AttribError'

    # ElementBlockInterface implementation
    def get_content_as_text(self):
    #    buf = self.get_buffer()
    #    assert(buf is not None)
    #    return buf.get_content_as_text()
        pass

    def set_content_from_html(self, text):
    #    buf = self.get_buffer()
    #    assert(buf is not None)
    #    return buf.set_content_from_html(text)
        pass

    def get_content_as_html(self):
    #    buf = self.get_buffer()
    #    assert(buf is not None)
    #    return buf.get_content_as_html()
        pass

    def get_serialize_tag_name(self):
        return 'img'

    def is_deletable(self):
    #    buf = self.get_buffer()
    #    start = buf.get_start_iter()
    #    end = buf.get_end_iter()
    #    return start.compare(end) == 0
        return True

    def load_image_from_file(self, filename):
        img = Gtk.Image.new_from_file(filename)
        img.show()
        assert(self.childwidget is None)
        self.childwidget = img
        self.childwidget_posx = 0
        self.childwidget_posy = 0
        self.add(img)

        w, _dont_care_ = img.get_preferred_width()
        h, _dont_care_ = img.get_preferred_height()
        self.img = img
        #self.set_hexpand(False)
        #self.set_vexpand(False)
        self.set_size_request(w, h)
        #self.set_size(w, h)

    #def on_key_press_event(self, window, event):
    #    key = Gdk.keyval_name(event.keyval)

    #    # debug string :
    #    #print(key + str(event.state))

    #    if event.state & Gdk.ModifierType.CONTROL_MASK and key in ('o', 's', 'v'):
    #        if key == 'v':
    #            pixbuf = self.clipboard.wait_for_image()
    #            visid = self.textbuffer_visibleid
    #            if pixbuf != None and visid != -1:
    #                self.textbuffers[visid].insert_pixbuf_at_cursor(pixbuf)
    #            else:
    #                return False

    #            #print ('event catched')
    #            return True

    #    return False

GObject.type_register(ImageView)

