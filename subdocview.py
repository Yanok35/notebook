#!/usr/bin/env python

# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import cairo
from gi.repository import Gdk, GObject, Gtk, Pango, PangoCairo
from lxml import etree

from ielementblock import ElementBlockInterface
from editortextview import EditorTextView
from editortextbuffer import EditorTextBuffer
from imageview import ImageView
from imagemodel import ImageModel

class SubdocView(Gtk.Container):
    __gtype_name__ = 'SubdocView'

    PARAGRAPH = 1
    IMAGE = 2

    # 'Static' class members
    block_insert_btn = None
    block_remove_btn = None
    block_change_combo = None
    ignore_combo_signal = False

    block_in_focus = None

    # toolbar handling using class methods
    @classmethod
    def toolbar_create(cls, toolbar, self):
        if cls.block_insert_btn is None:
            cls.block_insert_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_NEW)
            cls.block_insert_btn.show()
            toolbar.insert(cls.block_insert_btn, -1)

        if cls.block_remove_btn is None:
            cls.block_remove_btn = Gtk.ToolButton.new_from_stock(Gtk.STOCK_REMOVE)
            cls.block_remove_btn.show()
            toolbar.insert(cls.block_remove_btn, -1)

        if cls.block_change_combo is None:
            model = Gtk.ListStore(GObject.TYPE_INT, GObject.TYPE_STRING)
            model.append([SubdocView.PARAGRAPH, "Paragraph"])
            model.append([SubdocView.IMAGE, "Image"])
            cls.block_change_combo = Gtk.ComboBox.new_with_model_and_entry(model)
            cls.block_change_combo.set_entry_text_column(1)
            cls.block_change_combo.set_active(0) # 1st row

            item = Gtk.ToolItem.new()
            item.add(cls.block_change_combo)
            item.show_all()
            toolbar.insert(item, -1)

            sep = Gtk.SeparatorToolItem()
            sep.show()
            toolbar.insert(sep, -1)

        cls.block_insert_btn.connect('clicked', self.on_block_insert_clicked)
        cls.block_remove_btn.connect('clicked', self.on_block_remove_clicked)
        self.sigid_block_combo_changed = \
        cls.block_change_combo.connect('changed', self.on_combo_block_changed)

    def __init__(self, elements_toolbar):
        Gtk.Container.__init__(self)

        self.add_events(Gdk.EventMask.KEY_PRESS_MASK)

        self.childrens = {} # list of block elements
        self.nb_blocks = 0
        self.cursor_idx = 0 # index of currently focused block element

        self.set_has_window(False)
        self.set_border_width(10) # for debug only

        self.elements_toolbar = elements_toolbar
        assert(self.elements_toolbar is not None)
        SubdocView.toolbar_create(elements_toolbar, self)

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

    def do_draw(self, ctx):
        ctx.save()
        rect = self.get_allocation()
        ctx.translate(-rect.x, -rect.y) # to match Gtk absolute coord

        # Draw a background
        #ctx.set_source_rgb(1, 1, 1) # white
        ctx.set_source_rgb(0.9, 0.9, 0.9) # grey90
        ctx.paint()
        ctx.set_source_rgb(0, 0, 0) # black

        # # Cross for layout debugging
        # ctx.set_line_width(1)
        # ctx.move_to(rect.x, rect.y)
        # ctx.line_to(rect.x + rect.width, rect.y + rect.height)
        # ctx.move_to(rect.x + rect.width, rect.y)
        # ctx.line_to(rect.x, rect.y + rect.height)
        # ctx.stroke()

        # Blue rectangle to outline childrens (debug also)
        #ctx.save()
        for docid, child in self.childrens.items():
            if not child.get_visible():
                continue
            rect = child.get_allocation()
            if child.is_focus():
                ctx.set_line_width(4)
            else:
                ctx.set_line_width(1)
            ctx.set_source_rgb(0, 0, 1) # blue
            ctx.rectangle(rect.x, rect.y, rect.width, rect.height)
            ctx.stroke()
            #print (rect.x, rect.y, rect.width, rect.height)
        #ctx.restore()

        ctx.restore()

        Gtk.Container.do_draw(self, ctx)
        return False

    def do_key_press_event(self, event):
        #print("key_press_event in subdocview")
        key = Gdk.keyval_name(event.keyval)
        if key == 'Return':
            print("todo: check block items focused, catch cursor and split if needed")
            self.block_add_after_cursor()
            return True
            ### w = self.block_add_at_end(block_type = SubdocView.IMAGE)
            ### #w.load_image_from_file("oshw-logo-800-px.png")
            ### w.load_image_from_file("Firefox_Old_Logo_small.png")
            ### return True
        elif key =='BackSpace':
            if self.nb_blocks > 0 and self.cursor_idx != 0:
                self.block_remove(self.cursor_idx)

        return Gtk.Container.do_key_press_event(self, event)

    # Gtk.Container methods override
    def do_child_type(self):
        return ElementBlockInterface

    def do_add(self, widget):
        widget.set_parent(self)

    def do_remove(self, widget):
        for key, val in self.childrens.items():
            if val == widget:
                widget.unparent()
                self.queue_resize()

    def do_forall(self, include_int, callback):
        try:
            for docid, widget in self.childrens.items():
                callback(widget)
        except AttributeError:
            pass # print 'AttribError'

    # Signals (mostly from childs)
    def on_child_focus_in(self, widget, event):
        #print('on_child_focus_in', widget, event)

        # Class variable to store this reference
        SubdocView.block_in_focus = widget

        # Update combo block to match the subclass
        SubdocView.ignore_combo_signal = True
        clsname = widget.__class__.__name__
        if clsname == 'EditorTextView':
            SubdocView.block_change_combo.set_active(0)
        elif clsname == 'ImageView':
            SubdocView.block_change_combo.set_active(1)
        else:
            raise AttributeError
        SubdocView.ignore_combo_signal = False

        # Find widget in list and put cursor_idx up to date
        for key, child in self.childrens.items():
            if child == widget:
                self.cursor_idx = key

        # We should redraw the projectview widget. parent of subdocview
        # TODO: find another way to propagate this ?
        self.get_parent().queue_draw()

    def on_child_cursor_move(self, widget, direction):
        #print('on_child_cursor_move', widget, direction)
        #print('   idx = %d in list : ' % self.cursor_idx, self.childrens.items())
        prev_index = self.cursor_idx
        if direction == ElementBlockInterface.CursorDirection.UP:
            if self.cursor_idx > 0:
                self.cursor_idx -= 1
        elif direction == ElementBlockInterface.CursorDirection.DOWN:
            if self.nb_blocks and self.cursor_idx < self.nb_blocks - 1:
                self.cursor_idx += 1

        if self.cursor_idx != prev_index:
            self.childrens[self.cursor_idx].grab_focus()
            self.get_parent().queue_draw()

    def on_block_insert_clicked(self, btn):
        if self.get_focus_child():
            #print('insert_at %d', self.cursor_idx)
            self.block_add_at_index(self.cursor_idx)

    def on_block_remove_clicked(self, btn):
        if self.get_focus_child():
            #print('on_block_remove_clicked')
            #if self.childrens[self.cursor_idx].is_focus():
            if self.nb_blocks > 0 and self.cursor_idx != 0:
                self.block_remove(self.cursor_idx)

    def on_combo_block_changed(self, combo):
        #print("combo is now", combo.get_active())
        if not SubdocView.ignore_combo_signal:
            child = SubdocView.block_in_focus
            if child and child.get_parent() == self:
                for blockid, widget in self.childrens.items():
                    if widget == child:
                        #print('will add/remove/add')
                        if combo.get_active() == SubdocView.PARAGRAPH - 1:
                            self.block_add_at_index(blockid, block_type = SubdocView.PARAGRAPH)
                        elif combo.get_active() == SubdocView.IMAGE - 1:
                            self.block_add_at_index(blockid, block_type = SubdocView.IMAGE)
                        self.block_remove(blockid+1)

    # Application accessors
    def _block_new(self, block_type = PARAGRAPH):
        #print("_block_new:")
        if block_type == SubdocView.PARAGRAPH:
            buf = EditorTextBuffer()
            widget = EditorTextView(self.elements_toolbar)
            widget.set_buffer(buf)
            self.add(widget)
        elif block_type == SubdocView.IMAGE:
            #print("Image insertion asked")
            widget = ImageView()
            self.add(widget)
            model = ImageModel()
            widget.set_model(model)
        else:
            raise NotImplementedError

        widget.connect("focus-in-event", self.on_child_focus_in)
        widget.connect("cursor-move", self.on_child_cursor_move)

        #self.add(widget)

        return widget

    def block_add_at_end(self, **args):
        return self.block_add_at_index(self.nb_blocks, **args)

    def block_add_at_index(self, index, **args):
        assert(index >= 0 and index <= self.nb_blocks)

        # chain element at 'index' pos in childrens list.
        for i in list(reversed(range(index, self.nb_blocks))):
            self.childrens[i+1] = self.childrens[i]

        block = self._block_new(**args)
        self.childrens[index] = block
        self.nb_blocks += 1

        # self.cursor_idx will be updated in signal "focus-in-event"
        block.grab_focus()
        self.queue_resize()

        return block

    def block_add_after_cursor(self, **args):
        return self.block_add_at_index(self.cursor_idx + 1, **args)

    def block_remove(self, index):
        assert(index >= 0 and index <= self.nb_blocks)

        self.remove(self.childrens[index])
        del self.childrens[index]

        #from IPython import embed
        #embed()

        # move elements after 'index', *up* in the childrens list.
        shift_occured = False
        for i in range(index, self.nb_blocks - 1):
            self.childrens[i] = self.childrens[i+1]
            shift_occured = True

        if shift_occured:
            del self.childrens[self.nb_blocks - 1]
        self.nb_blocks -= 1

        if self.cursor_idx >= index and self.cursor_idx > 0:
            self.cursor_idx -= 1
            self.childrens[self.cursor_idx].grab_focus()

        self.queue_resize()

    def block_remove_all(self):
        while self.nb_blocks:
            self.block_remove(self.nb_blocks - 1)

    def load_from_file(self, filename):

        self.block_remove_all()

        with open(filename, 'r') as f:
            data = f.read()
            data = data.decode('utf-8')

            # Parse XML file to add node recursively
            subdoc = etree.fromstring(data)
            assert(subdoc.tag == 'subdoc')

            for child in subdoc:
                if child.tag == 'p':
                    widget = self.block_add_at_end(block_type = SubdocView.PARAGRAPH)
                elif child.tag == 'img':
                    widget = self.block_add_at_end(block_type = SubdocView.IMAGE)

                widget.set_element_serialized(child.text)

    def save_to_file(self, filename):
        subdoc = etree.Element('subdoc')
        tree = etree.ElementTree(subdoc)
        for docid, child in self.childrens.items():
            tag_name = child.get_serialize_tag_name()
            childnode = etree.SubElement(subdoc, tag_name)
            try:
                childnode.text = child.get_element_serialized()
            except NotImplementedError:
                print ('*** Warning: Element ' + str(child) + ' does not support serialize')
        with open(filename, 'w') as f:
            tree.write(f, pretty_print=True)

    def get_content_as_text(self):
        text = ''
        for i in range(0, self.nb_blocks):
            text += self.childrens[i].get_content_as_text()
            if not text.endswith('\n'):
                text += '\n'
            text += '\n'
        return text

GObject.type_register(SubdocView)
