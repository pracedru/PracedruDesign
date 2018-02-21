from PyQt5.QtCore import QCoreApplication, QLocale
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QWidget

from Data import write_data_to_disk


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


contexts = {}


def tr(string, context_name='app'):
    value = QCoreApplication.translate(context_name, string)
    try:
        context = contexts[context_name]
    except KeyError:
        contexts[context_name] = {}
        context = contexts[context_name]
    context[string] = value
    return value


def write_language_file():
    from lxml import etree
    ts_elem = etree.Element("TS", version="2.0", language=QLocale().name(), sourcelanguage="en")
    doc = etree.ElementTree(ts_elem)
    for context_tuple in contexts.items():
        context_elem = etree.SubElement(ts_elem, "context")
        name_elem = etree.SubElement(context_elem, "name")
        name_elem.text = context_tuple[0]
        for message_tuple in context_tuple[1].items():
            message_elem = etree.SubElement(context_elem, "message")
            source_elem = etree.SubElement(message_elem, "source")
            translation_elem = etree.SubElement(message_elem, "translation")
            source_elem.text = message_tuple[0]
            translation_elem.text = message_tuple[1]

    text = etree.tostring(ts_elem, pretty_print=False, xml_declaration=True, encoding="UTF-8", doctype="<!DOCTYPE TS>")
    text = str(text, 'utf-8')
    text = text.replace("\n", "&#xA;")
    text = text.replace(">&#xA;<", "><")
    write_data_to_disk("%s.ts" % QLocale().name(), text)

def formula_from_locale(formula):
  locale = QLocale()
  if locale.decimalPoint() == ",":
    return formula.replace(",", ".").replace(";", ",")
  return formula


def formula_to_locale(formula):
    locale = QLocale()
    if locale.decimalPoint() == ",":
        return formula.replace(",", ";").replace(".", ",")
    return formula

