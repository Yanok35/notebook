#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import GObject, Gtk

# Interface definition
class ElementBlockInterface(object):
    __gsignals__ = {
        str('cursor-move'): (GObject.SIGNAL_RUN_FIRST, None, (int,)),
    }

    class CursorDirection:
        UP = 1
        DOWN = 2

    # On screen UI and rendering
    def is_deletable(self):
        raise NotImplementedError

    def get_content_as_html(self):
        raise NotImplementedError

    def set_content_from_html(self, html):
        raise NotImplementedError

    def get_content_as_text(self):
        raise NotImplementedError

    def get_serialize_tag_name(self):
        raise NotImplementedError

    def get_element_serialized(self):
        raise NotImplementedError

    def set_element_serialized(self, data):
        raise NotImplementedError

    # On PDF rendering
    def get_pages_required_for_rendering(self, w, h):
        ''' given a width, height, the block element should return
        number of call to draw_on_cairo_surface required if does not fit
        in one page'''
        raise NotImplementedError

    def draw_on_cairo_surface(self, ctx, x, y, w, h, part_number = 0):
        raise NotImplementedError

