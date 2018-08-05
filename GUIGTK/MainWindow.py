import pgi

pgi.require_version('Gtk', '3.0')
pgi.install_as_gi()
from gi.repository import Gtk


class MainWindow(Gtk.Window):
	def __init__(self, document):
		Gtk.Window.__init__(self, title="Pracedru Design")
		self._doc = document
		self.set_default_size(1280, 800)
