#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from gi.repository import GObject, Gtk

# Interface definition
class ElementBlockInterface(Gtk.Widget):
    def __init__(self):
        Gtk.Widget.__init__(self)

    def is_deletable(self):
        raise NotImplemented

    def get_content_as_html(self):
        raise NotImplemented

    def get_serialize_tag_name(self):
        raise NotImplemented

    def get_content_as_text(self):
        raise NotImplemented

    def set_content_from_html(self, html):
        raise NotImplemented

GObject.type_register(ElementBlockInterface)

