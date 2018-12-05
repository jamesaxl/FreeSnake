import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango, Gdk

class ChatView(Gtk.TextView):

    def __init__(self):
        Gtk.TextView.__init__(self)
        self.set_editable(False)

        self.chat_buffer = self.get_buffer()
        self.set_cursor_visible(False)
        self.set_wrap_mode(Gtk.WrapMode.WORD)
        self.modify_font(Pango.FontDescription("monospace 10.5"))

        self.tag_url = self.chat_buffer.create_tag(None, underline=Pango.Underline.SINGLE, foreground ='blue')
        self.tag_url.set_property("underline",Pango.Underline.SINGLE)

    def put_msg(self, message):
        self.chat_buffer.set_text(message)
        self.chat_buffer.set_text('\n')