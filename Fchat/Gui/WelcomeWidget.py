import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class WelcomeWidget(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, spacing=6, orientation = Gtk.Orientation.VERTICAL)
        
        welcome_lb = Gtk.Label()
        welcome_lb.set_markup("Freenet is a peer-to-peer platform for censorship-resistant communication and publishing."
                         "Fchat is a Gui application that you can use to chat with friends."
                         "\n<big><b>Note:</b> Do not share you personal info with anyone, to be safe try to chat and add only Friends</big>\n"
                         "<a href=\"https://github.com/jamesaxl/FreeSnake\" "
                         "title=\"project Repos\">more info about our project FreeSnake</a>.")

        welcome_lb.set_line_wrap(True)

        self.pack_start(welcome_lb, True, True, 0)
