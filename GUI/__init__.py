from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget


def gui_scale():
    screen = QApplication.screens()[0];
    dpi = screen.logicalDotsPerInch()
    return dpi / 96


def is_dark_theme():
    widget = QWidget()
    color = widget.palette().color(widget.backgroundRole())
    r = 0.0
    g = 0.0
    b = 0.0
    a = 0.0
    rgb = color.getRgb()
    if (rgb[0]+rgb[1]+rgb[2]) < 300:
        return True
    else:
        return False

stylesheet_instance = None


def get_stylesheet(name):
    global stylesheet_instance
    if not stylesheet_instance:
        stylesheet_instance = Stylesheets()
    return stylesheet_instance.stylesheet(name)


class Stylesheets(object):
    def __init__(self):
        self._stylesheets = {}
        self.make_stylesheet("main", "stylesheets/main.css")
        self.make_stylesheet("ribbon", "stylesheets/ribbon.css")
        self.make_stylesheet("ribbon_dark", "stylesheets/ribbon_dark.css")
        self.make_stylesheet("ribbonPane", "stylesheets/ribbonPane.css")
        self.make_stylesheet("ribbonButton", "stylesheets/ribbonButton.css")
        self.make_stylesheet("ribbonSmallButton", "stylesheets/ribbonSmallButton.css")

    def make_stylesheet(self, name, path):
        with open(path) as data_file:
            stylesheet = data_file.read()

        self._stylesheets[name] = stylesheet

    def stylesheet(self, name):
        stylesheet = ""
        try:
            stylesheet = self._stylesheets[name]
        except KeyError:
            print("stylesheet " + name + " not found")
        return stylesheet
