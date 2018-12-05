import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

class AddFriendWidget(Gtk.Box):

    def __init__(self):
        Gtk.Box.__init__(self, spacing=7, orientation = Gtk.Orientation.VERTICAL)
        self.ksk  = Gtk.Entry()

        note_lb = Gtk.Label()
        note_lb.set_markup("Freenet is a peer-to-peer platform for censorship-resistant communication and publishing."
                         "Fchat is a Gui application that you can use to chat with friends."
                         "\n<big><b>Note:</b> Do not share you personal info with anyone, to be safe try to chat and add only Friends</big>\n"
                         "<a href=\"https://github.com/jamesaxl/FreeSnake\" "
                         "title=\"project Repos\">more info about our project FreeSnake</a>.")

        note_lb.set_line_wrap(True)

        self.ksk.set_placeholder_text('KSK@')
        
        self.pack_start(self.ksk, True, False, 7) 
