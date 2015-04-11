#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import Gdk, GdkPixbuf, GObject, Gtk

#from ielementblock import ElementBlockInterface

class ImageModel(GObject.GObject):
    __gtype_name__ = 'ImageModel'

    __gsignals__ = {
        str('image-changed'): (GObject.SIGNAL_RUN_FIRST, None, ()),
        str('move'): (GObject.SIGNAL_RUN_FIRST, None, (int, int)),
    }

    def __init__(self, **args):
        GObject.GObject.__init__(self, **args)

        self.imgsrc = None # Gtk.image
        self.imgdest = None

        self.filename = None
        self.format_str = ''

    # Public methods
    def load_from_file(self, filename):
        self.filename = filename
        self.imgsrc = Gtk.Image.new_from_file(filename)
        self.imgsrc.show()

        # no transform right now:
        self.imgdest = self.imgsrc
        self.emit('image-changed')

    def get_src_width(self):
        w = -1
        if self.imgsrc:
            w = self.imgsrc.get_pixbuf().get_width()
        return w

    def get_src_height(self):
        h = -1
        if self.imgsrc:
            h = self.imgsrc.get_pixbuf().get_height()
        return h

    def get_filename(self):
        return self.filename

    def set_image_coord(self, x, y):
        self.img_posx = x
        self.img_posy = y
        self.emit('move', x, y)
        #self.emit('image-changed')

    def get_image_coord(self):
        return (self.img_posx, self.img_posy)

    def get_image(self):
        return self.imgdest

GObject.type_register(ImageModel)

