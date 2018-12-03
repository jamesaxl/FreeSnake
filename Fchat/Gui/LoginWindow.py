import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, Gtk
from WelcomeWidget import WelcomeWidget
import sys

MENU_XML = """
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

class LoginWindow(Gtk.ApplicationWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_border_width(10)
        self.set_default_size(700, 500)

        menu_bt = Gtk.MenuButton.new()
        menu_builder = Gtk.Builder.new_from_string(MENU_XML, -1)
        main_menu = menu_builder.get_object("app-menu")
        popover = Gtk.Popover.new_from_model(menu_bt, main_menu)
        menu_bt.set_popover(popover)

        self.header_bar = Gtk.HeaderBar()
        self.header_bar.set_show_close_button(False)
        self.header_bar.props.title = "Freenet Fchat"
        self.header_bar.pack_end(menu_bt)

        self.set_titlebar(self.header_bar)

        menu_bt.show()
        self.header_bar.show()

class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, application_id="org.freenet.fchat", **kwargs)
        self.window = None
        self.welcome = None

    def do_startup(self):
        Gtk.Application.do_startup(self)

        action = Gio.SimpleAction.new("connect", None)
        action.connect("activate", self.on_connect)
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
        if not self.window:
            self.window = LoginWindow(application=self)
            self.welcome = WelcomeWidget()
            self.window.add(self.welcome)
            self.welcome.show_all()
        self.window.present()

    
    def on_connect(self, action, parameter):
        print('connect')

    def on_config(self, action, parameter):
        print('config')

    def on_about(self, action, parameter):
        about_dialog = Gtk.AboutDialog(transient_for=self.window, modal=True)
        authors = ["James Axl"]
        documenters = ["James Axl"]
        about_dialog.set_program_name("Freenet Barnamy")
        about_dialog.set_copyright(
            "CopyLeft 2018 James Axl")
        about_dialog.set_authors(authors)
        about_dialog.set_documenters(documenters)
        about_dialog.set_website("https://freenetproject.org/")
        about_dialog.set_website_label("Freenet Website")
        about_dialog.set_title("")
        about_dialog.connect("response", self.on_close)
        about_dialog.show()

    def on_close(self, action, parameter):
        action.destroy()

    def on_quit(self, action, param):
        self.quit()

app = Application()
app.run(sys.argv)