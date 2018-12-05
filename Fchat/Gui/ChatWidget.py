import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

from ChatView import ChatView
from ChatEntry import ChatEntry

class ChatWidget(Gtk.Notebook):

    def __init__(self, main_window, friends_widget):
        Gtk.Notebook.__init__(self)
        
        self.main_window = main_window
        self.friends_widget = friends_widget

        self.set_scrollable(True)
        self.popup_enable()

    def add_chat(self, friend):

        for page in self.get_children():
            if self.get_tab_label(page).get_children()[0].get_text() == friend:
                self.set_current_page(self.page_num(page))
                return

        close_bt = Gtk.Button('X')
        title_box = Gtk.Box(False, 6)

        title_box.add(Gtk.Label(friend))
        title_box.add(close_bt)

        chat_box = Gtk.Box(spacing=7, orientation = Gtk.Orientation.VERTICAL)
        chat_box.set_border_width(10)
        chat_view = ChatView()
        chat_entry = ChatEntry()
        scroll_view = Gtk.ScrolledWindow()
        scroll_view.add(chat_view)
        chat_box.pack_start(scroll_view, True, True, 0)
        chat_box.pack_start(chat_entry, False, False, 0)
        self.append_page(chat_box, title_box)

        self.show_all()
        title_box.show_all()

        self.set_current_page(-1)

        close_bt.connect('clicked', self.on_closetab_clicked, chat_box)

    def on_closetab_clicked(self, sender, widget):
        pagenum = self.page_num(widget)
        self.remove_page(pagenum)

        if self.get_n_pages() == 0:
            self.main_window.remove(self.main_window.get_children()[0])
            self.main_window.add(self.friends_widget)
            self.main_window.back_friend_list_bt.hide()
