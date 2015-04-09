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

