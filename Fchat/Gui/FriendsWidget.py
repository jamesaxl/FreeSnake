import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk
from .FriendsList import FriendsList

class FriendsWidget(Gtk.Box):

    def __init__(self, main_window, fchat_prv):
        Gtk.Box.__init__(self, spacing=7, orientation = Gtk.Orientation.VERTICAL)
        self.search_entry = Gtk.SearchEntry()
        
        self.fchat_prv = fchat_prv
        scroll_view = Gtk.ScrolledWindow()
        self.friend_list = FriendsList(main_window, self)

        scroll_view.add(self.friend_list)
        self.pack_start(self.search_entry, False, False, 0)
        self.pack_start(scroll_view, True, True, 0)

