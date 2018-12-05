import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

class ChatEntry(Gtk.Entry):

    def __init__(self):
        Gtk.Entry.__init__(self)

    def send_msg(self, text):
        pass