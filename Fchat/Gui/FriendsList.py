import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk
from .ChatWidget import ChatWidget

STATUS = { 'online' : 0, 'away' : 1, 'offline' : 2 }

class FriendsList(Gtk.TreeView):
    
    def __init__(self, main_window, friends_widget):
        Gtk.TreeView.__init__(self)

        self.chat_widget = ChatWidget(main_window, friends_widget)

        self.main_window = main_window
        self.fchat_prv = friends_widget.fchat_prv

        self.liststore = Gtk.ListStore(str, str)
        self.set_model(self.liststore)

        friend_renderer_text = Gtk.CellRendererText()
        friend_column_text = Gtk.TreeViewColumn('friends', friend_renderer_text, text=0)

        status_renderer_text = Gtk.CellRendererText()
        status_column_text = Gtk.TreeViewColumn('status', status_renderer_text, text=1)

        status_column_text.set_sort_column_id(1)

        self.append_column(friend_column_text)
        self.append_column(status_column_text)

        self.selected_text = {}

        select = self.get_selection()
        select.connect('changed', self.on_tree_selection_changed)

        self.connect('row-activated', self.on_double_click)

        self.get_model().set_sort_func(1, self.compare, None)
        
        self.sync_friends_list()

    def on_double_click(self, tree_view, path, column):
        treeiter = tree_view.get_model().get_iter(path)
        value = tree_view.get_model().get_value(treeiter, 0)            

        self.chat_widget.add_chat(value)

        self.main_window.remove(self.main_window.get_children()[0])
        self.main_window.add(self.chat_widget)
        self.main_window.back_friend_list_bt.show()

        print('double click {}'.format(value))

    def sync_friends_list(self):
        friends = self.fchat_prv.get_friends()
        for friend in friends:
            self.fill_friends_list(friend, '')

    def fill_friends_list(self, friend, status):
        self.liststore.append([friend, status])

    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:

            row_num_obj = model.get_path(treeiter)
            row_num = int(row_num_obj.to_string())

            self.selected_text['friend'] = model[treeiter][0]
            self.selected_text['status'] = model[treeiter][1]
            self.selected_text['iter'] = treeiter
            self.selected_text['path'] = row_num_obj
            self.selected_text['position'] = row_num
            self.selected_text['selection'] = selection

    def compare(self, model, row1, row2, user_data):
        sort_column, _ = model.get_sort_column_id()
        value1 = model.get_value(row1, sort_column)
        value2 = model.get_value(row2, sort_column)

        if STATUS[value1] < STATUS[value2]:
            return -1
        elif value1 == value2:
            return 0
        else:
            return 1
