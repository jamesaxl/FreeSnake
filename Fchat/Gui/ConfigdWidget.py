import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk

class ConfigdWidget(Gtk.Box):

    def __init__(self, main_window = None, fchat_base = None):
        Gtk.Box.__init__(self, spacing=7, orientation = Gtk.Orientation.VERTICAL)

        self.main_window = main_window
        self.fchat_base = fchat_base
        
        self.host  = Gtk.Entry()
        self.port  = Gtk.Entry()
        self.name_of_connection  = Gtk.Entry()
        self.engine_mode = Gtk.ComboBoxText()
        self.verbosity = Gtk.ComboBoxText()
        self.log_type = Gtk.ComboBoxText()
        
        self.host.set_placeholder_text('Host')
        self.port.set_placeholder_text('Port')

        self.engine_mode.append_text('--Engine Mode--')
        self.engine_mode.append_text('socket')
        self.engine_mode.append_text('wsocket')
        
        self.save_bt = Gtk.Button('Save')
        self.save_bt.connect('clicked', self.set_config)
        
        self.cancel_bt = Gtk.Button('Cancel')
        self.cancel_bt.connect('clicked', self.on_cancel)
        
        h_bt = Gtk.Box(spacing = 6)
        h_bt.pack_start(self.save_bt, True, True, 3)
        h_bt.pack_start(self.cancel_bt, True, True, 3)
                        
        self.pack_start(self.host, True, False, 7)
        self.pack_start(self.port, True, False, 7)
        self.pack_start(self.name_of_connection, True, False, 7)
        self.pack_start(self.engine_mode, True, False, 7) 
        self.pack_start(h_bt, True, False, 7)

    def set_config(self, button):
        
        if not self.host.get_text():
            self.msg_info('Host is required')
            return

        if not self.port.get_text():
            self.msg_info('Port is required')
            return

        if not self.name_of_connection.get_text():
            self.msg_info('Name of connection is required')
            return

        if self.engine_mode.get_active() == 0:
            self.msg_info('Engine mode is required')
            return

        self.fchat_base.set_config( host = self.host.get_text(), port = self.port.get_text(), 
                         name_of_connection = self.name_of_connection.get_text(), 
                         engine_mode = self.engine_mode.get_active_text())

        self.main_window.application.back_main_window_or_friend_list()

    def get_config(self):
        conf = self.fchat_base.get_config()

        self.log_path = conf['log_path']
        self.host.set_text(conf['host'])
        self.port.set_text(conf['port'])
        self.name_of_connection.set_text(conf['name_of_connection'])
        
        if conf['engine_mode'] == 'socket':
            self.engine_mode.set_active(1)
        
        elif conf['engine_mode'] == 'wsocket':
            self.engine_mode.set_active(2)

    def on_cancel(self, button):
        self.main_window.application.back_main_window_or_friend_list()

    def msg_info(self, text):
        dialog = Gtk.MessageDialog(self.main_window, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Info")
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()
