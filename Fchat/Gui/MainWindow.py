import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk
from WelcomeWidget import WelcomeWidget
from FriendsWidget import FriendsWidget
from AddFriendWidget import AddFriendWidget
import sys

MENU_OFF = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
        <item>
            <attribute name="label">Connect</attribute>
            <attribute name="action">app.connect</attribute>
        </item>


        <item>
            <attribute name="label">Config</attribute>
            <attribute name="action">app.config</attribute>
        </item>
        <item>
            <attribute name="label">About</attribute>
            <attribute name="action">app.about</attribute>
        </item>
        <item>
            <attribute name="label">Quit</attribute>
            <attribute name="action">app.quit</attribute>
        </item>
    </section>
  </menu>
</interface>
"""

MENU_ON = """
<?xml version="1.0" encoding="UTF-8"?>
<interface>
  <menu id="app-menu">
    <section>
        <item>
            <attribute name="label">Disconnect</attribute>
            <attribute name="action">app.disconnect</attribute>
        </item>

        <item>
            <attribute name="label">Add Friend</attribute>
            <attribute name="action">app.add_friend</attribute>
        </item>

        <item>
            <attribute name="label">Config</attribute>
            <attribute name="action">app.config</attribute>
        </item>
        <item>
            <attribute name="label">About</attribute>
            <attribute name="action">app.about</attribute>
        </item>
        <item>
            <attribute name="label">Quit</attribute>
            <attribute name="action">app.quit</attribute>
        </item>
    </section>
  </menu>
</interface>
"""

class MainWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_border_width(10)
        self.set_default_size(700, 500)

        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_show_close_button(False)
        self.header_bar.props.title = "Freenet Fchat"

        self.back_friend_list_bt = Gtk.Button('<-')
        self.header_bar.pack_start(self.back_friend_list_bt)

        self.set_titlebar(self.header_bar)

        self.menu_off()

        self.header_bar.show()

    def menu_off(self):
        menu_bt = Gtk.MenuButton.new()
        menu_builder = Gtk.Builder.new_from_string(MENU_OFF, -1)
        
        main_menu = menu_builder.get_object("app-menu")
        popover = Gtk.Popover.new_from_model(menu_bt, main_menu)
        menu_bt.set_popover(popover)
        self.header_bar.pack_end(menu_bt)
        menu_bt.show()


    def menu_on(self):
        menu_bt = Gtk.MenuButton.new()
        menu_builder = Gtk.Builder.new_from_string(MENU_ON, -1)
        
        main_menu = menu_builder.get_object("app-menu")
        popover = Gtk.Popover.new_from_model(menu_bt, main_menu)
        menu_bt.set_popover(popover)
        self.header_bar.pack_end(menu_bt)
        menu_bt.show()

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.freenet.fchat", **kwargs)
        self.main_window = None
        self.welcome_widget = None
        self.friends_widget = None
        self.add_friend_widget = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("connect", None)
        action.connect("activate", self.on_connect)
        self.add_action(action)

        action = Gio.SimpleAction.new("disconnect", None)
        action.connect("activate", self.on_disconnect)
        self.add_action(action)

        action = Gio.SimpleAction.new("add_friend", None)
        action.connect("activate", self.on_add_friend)
        self.add_action(action)

        action = Gio.SimpleAction.new("config", None)
        action.connect("activate", self.on_config)
        self.add_action(action)

        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)

        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)

    def do_activate(self):
        if not self.main_window:
            self.main_window = MainWindow(application=self)
            self.main_window.back_friend_list_bt.connect('clicked', self.back_friend_list)

            self.welcome_widget = WelcomeWidget()
            self.main_window.add(self.welcome_widget)
            self.welcome_widget.show_all()
        self.main_window.present()

    def on_connect(self, action, parameter):
        self.friends_widget = FriendsWidget(self.main_window)
        self.add_friend_widget = AddFriendWidget()
        self.main_window.remove(self.main_window.get_children()[0])
        self.main_window.add(self.friends_widget)
        self.friends_widget.show_all()

        self.main_window.header_bar.remove(self.main_window.header_bar.get_children()[-1])

        self.main_window.menu_on()

        print('connect')

    def on_add_friend(self, action, parameter):
        self.main_window.remove(self.main_window.get_children()[0])
        self.main_window.add(self.add_friend_widget)
        self.add_friend_widget.show_all()
        self.main_window.back_friend_list_bt.show()
        print('Add Friend')

    def on_disconnect(self, action, parameter):
        self.main_window.remove(self.main_window.get_children()[0])
        self.main_window.add(self.welcome_widget)
        self.friends_widget.show_all()

        self.main_window.header_bar.remove(self.main_window.header_bar.get_children()[-1])

        self.main_window.menu_off()
        print('disconnect')

    def on_config(self, action, parameter):
        print('config')

    def on_about(self, action, parameter):
        about_dialog = Gtk.AboutDialog(transient_for=self.main_window, modal=True)
        authors = ["James Axl"]
        documenters = ["James Axl"]
        about_dialog.set_program_name('Freenet Fchat')
        about_dialog.set_copyright('CopyLeft 2018 James Axl')
        about_dialog.set_authors(authors)
        about_dialog.set_documenters(documenters)
        about_dialog.set_website("https://freenetproject.org/")
        about_dialog.set_website_label("Freenet Website")
        about_dialog.set_title("")
        about_dialog.connect("response", self.on_close)
        about_dialog.show()

    def back_friend_list(self, button):
        self.main_window.remove(self.main_window.get_children()[0])
        self.main_window.add(self.friends_widget)
        button.hide()

    def on_close(self, action, parameter):
        action.destroy()

    def on_quit(self, action, param):
        self.quit()

app = Application()
app.run(sys.argv)
