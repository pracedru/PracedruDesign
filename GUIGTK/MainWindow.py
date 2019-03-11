
from gi.repository import Gtk, Gio


class MainWindow(Gtk.Window):
	def __init__(self, document):
		Gtk.Window.__init__(self, title="Pracedru Design")
		self._doc = document
		self.set_default_size(1280, 800)
		icon = Gio.ThemedIcon(name="document-new")
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		self.set_icon(image.get_pixbuf())

		hb = Gtk.HeaderBar()
		hb.set_show_close_button(True)
		hb.props.title = self.get_title()
		self.set_titlebar(hb)


		main_buttons = Gtk.Grid()
		main_buttons.add(self.create_button("document-new", self.on_new_button))
		main_buttons.add(self.create_button("document-open", self.on_open_button))
		main_buttons.add(self.create_button("document-save", self.on_open_button))
		main_buttons.add(self.create_button("document-save-as", self.on_open_button))
		main_buttons.add(self.create_button("edit-undo", self.on_open_button))
		main_buttons.add(self.create_button("edit-redo", self.on_open_button))

		hb.pack_start(main_buttons)

		end_buttons = Gtk.Grid()
		end_buttons.add(self.create_button("document-properties", self.on_open_button))
		hb.pack_end(end_buttons)

		self.box = Gtk.Box(spacing=6)
		self.add(self.box)

		self.button1 = Gtk.Button(label="Hello")
		self.button1.connect("clicked", self.on_button1_clicked)
		self.box.pack_start(self.button1, True, True, 0)

		self.button2 = Gtk.Button(label="Goodbye")
		self.button2.connect("clicked", self.on_button2_clicked)
		self.box.pack_start(self.button2, True, True, 0)

	def create_button(self, icon_name, button_callback):
		button = Gtk.Button()
		icon = Gio.ThemedIcon(name=icon_name)
		image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
		button.add(image)
		button.connect("clicked", button_callback)
		return button

	def on_new_button(self, widget):
		print("new")

	def on_open_button(self, widget):
		print("open")

	def on_button1_clicked(self, widget):
		print("Hello")

	def on_button2_clicked(self, widget):
		print("Goodbye")

