import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

class OwnerInfoWidget(Gtk.Box):

    def __init__(self, main_window = None, fchat_base = None):
        Gtk.Box.__init__(self, spacing=7, orientation = Gtk.Orientation.VERTICAL)

        self.main_window = main_window
        self.fchat_base = fchat_base

        self.name = Gtk.Entry()
        
        self.save_bt = Gtk.Button('Save')
        self.save_bt.connect('clicked', self.set_info)
        
        self.cancel_bt = Gtk.Button('Cancel')
        self.cancel_bt.connect('clicked', self.on_cancel)

        h_bt = Gtk.Box(spacing = 6)
        h_bt.pack_start(self.save_bt, True, True, 3)
        h_bt.pack_start(self.cancel_bt, True, True, 3)

        self.pack_start(self.name, True, False, 7)
        self.pack_start(h_bt, True, False, 7)

    def set_info(self, button):
        if self.name.get_sensitive():
            if self.name.get_text() == '':
                self.msg_info('Name is required')
                return

        self.fchat_base.generate_info(self.name.get_text())
        self.main_window.application.back_main_window_or_friend_list()

    def get_info(self):        
        if self.fchat_base.get_info():
            self.name.set_text(self.fchat_base.get_info()['OWNER'])
            self.name.set_sensitive(False)

    def on_cancel(self, button):
        self.main_window.application.back_main_window_or_friend_list()

    def msg_info(self, text):
        dialog = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Info")
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()
