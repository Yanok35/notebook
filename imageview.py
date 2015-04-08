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
            self.dialog_edit_image_property()
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

                pixbuf = self.img_orig.get_pixbuf()
                new_pixbuf = pixbuf.scale_simple(
                    rect.width + dX, rect.height + dY, GdkPixbuf.InterpType.BILINEAR)
                new_img = Gtk.Image.new_from_pixbuf(new_pixbuf)
                new_img.show()
                self.remove(self.childwidget)
                self.add(new_img)
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
            # do_motion_notify_event() while button1 inactive.
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
        self.img_orig = img
        #self.set_hexpand(False)
        #self.set_vexpand(False)
        self.set_size_request(w, h)
        #self.set_size(w, h)

    def dialog_edit_image_property(self):
        builder = Gtk.Builder.new_from_file("imageview.ui")
        builder.connect_signals(self)
        self.dialog = builder.get_object('dialog_img_properties')

        # This call is blocking until user close the dialog.
        response = self.dialog.run()
        #if response == Gtk.ResponseType.OK:

        self.dialog.destroy()
        self.dialog = None

    def on_dialog_button_close_clicked(self, btn):
        print("close")
        self.dialog.response(Gtk.ResponseType.OK)

        pass

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

