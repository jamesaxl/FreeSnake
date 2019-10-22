import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk, Gdk

class AddFriendWidget(Gtk.Box):

    def __init__(self, main_window, fchat_prv, friend_list):
        Gtk.Box.__init__(self, spacing=7, orientation = Gtk.Orientation.VERTICAL)

        self.fchat_prv = fchat_prv
        self.main_window = main_window
        self.friend_list = friend_list

        self.fchat_prv.add_friend_gui = self

        self.generate_keys_bt = Gtk.Button('Generate Key')
        self.generate_keys_bt.connect('clicked', self.on_generate_keys)

        self.save_bt = Gtk.Button('Save')
        self.save_bt.connect('clicked', self.on_save)

        self.cancel_bt = Gtk.Button('Cancel')
        self.cancel_bt.connect('clicked', self.on_cancel)

        self.close_bt = Gtk.Button('Close')
        self.close_bt.connect('clicked', self.on_close)

        self.owner_info  = Gtk.Entry()
        self.owner_info.set_sensitive(False)
        
        self.copy_clipboard_bt = Gtk.Button(label='Copy to clipboard')
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self.copy_clipboard_bt.connect('clicked', self.on_copy_clipboard)
        
        h_owner = Gtk.Box(spacing=5)
        h_owner.pack_start(self.owner_info, True, True, 1)
        h_owner.pack_start(self.copy_clipboard_bt, False, False, 1)

        self.friend_info  = Gtk.Entry()
        self.friend_info.set_placeholder_text('Key of your friend')
        self.spinner = Gtk.Spinner()

        self.pack_start(h_owner, True, False, 7)
        self.pack_start(self.friend_info, True, False, 7)
        self.pack_start(self.spinner, True, False, 7)
        h_bt = Gtk.Box()
        h_bt.pack_start(self.generate_keys_bt, True, False, 7)
        h_bt.pack_start(self.save_bt, True, False, 7)
        h_bt.pack_start(self.cancel_bt, True, False, 7)
        h_bt.pack_start(self.close_bt, True, False, 7)
        self.pack_start(h_bt, True, False, 7)
        
        self.job = None

    def on_generate_keys(self, button):
        self.pub, self.prv, self.pub_info_key, self.job = self.fchat_prv.generate_key_for_friend()
        self.owner_info.set_text(self.pub_info_key)
        self.on_generate_keys_start()

    def on_generate_keys_start(self):
        self.spinner.show()
        self.spinner.start()
        self.friend_info.set_sensitive(False)
        self.save_bt.set_sensitive(False)
        self.close_bt.set_sensitive(False)
        self.generate_keys_bt.set_sensitive(False)
        self.copy_clipboard_bt.set_sensitive(False)

    def on_generate_keys_ok(self):
        self.spinner.hide()
        self.spinner.stop()
        self.friend_info.set_sensitive(True)
        self.save_bt.set_sensitive(True)
        self.close_bt.set_sensitive(True)
        self.generate_keys_bt.set_sensitive(True)
        self.copy_clipboard_bt.set_sensitive(True)

    def on_generate_keys_faild(self, text):

        self.spinner.hide()
        self.spinner.stop()
        self.friend_info.set_sensitive(True)
        self.save_bt.set_sensitive(True)
        self.close_bt.set_sensitive(True)
        self.generate_keys_bt.set_sensitive(True)
        self.copy_clipboard_bt.set_sensitive(True)

    def on_cancel(self, button):
        if self.job:
            self.job.remove_from_queue_when_finish()


    def on_close(self, button):
        self.main_window.application.back_main_window_or_friend_list()

    def on_save(self, button):
        if self.owner_info.get_text() == '':
            self.msg_info('You should generate a key that contains your info')
            return
        
        if self.friend_info.get_text() == '':
            self.msg_info('Friend info is required')
            return
        
        self.fchat_prv.add_friend(self.pub, self.prv, self.friend_info.get_text())
        
        self.on_save_start()

    def on_save_start(self):
        self.spinner.show()
        self.spinner.start()
        self.friend_info.set_sensitive(False)
        self.save_bt.set_sensitive(False)
        self.close_bt.set_sensitive(False)
        self.generate_keys_bt.set_sensitive(False)
        self.copy_clipboard_bt.set_sensitive(False)

    def on_save_start_ok(self):
        self.spinner.hide()
        self.spinner.stop()
        self.friend_info.set_sensitive(True)
        self.save_bt.set_sensitive(True)
        self.close_bt.set_sensitive(True)
        self.generate_keys_bt.set_sensitive(True)
        self.copy_clipboard_bt.set_sensitive(True)
        self.friend_list.sync_friends_list()

    def on_save_start_duplicate(self, text):
        self.msg_info(text)

    def on_save_start_faild(self):
        dialog = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "ERROR")
        dialog.format_secondary_text("Error adding friend please try later")
        dialog.run()
        dialog.destroy()

        self.spinner.hide()
        self.spinner.stop()
        self.friend_info.set_sensitive(True)
        self.save_bt.set_sensitive(True)
        self.close_bt.set_sensitive(True)
        self.generate_keys_bt.set_sensitive(True)
        self.copy_clipboard_bt.set_sensitive(True)

    def on_copy_clipboard(self, button):
        self.clipboard.set_text(self.owner_info.get_text(), -1)

    def msg_info(self, text):
        dialog = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Info")
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()
