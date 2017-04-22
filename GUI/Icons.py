from PyQt5.QtGui import *

__author__ = 'magnus'

icons_instance = None


def get_icon(name):
    global icons_instance
    if not icons_instance:
        icons_instance = Icons()
    return icons_instance.icon(name)


class Icons(object):
    def __init__(self):
        self._icons = {}
        self.make_icon("default", "icons/folder.png")

    def make_icon(self, name, path):
        icon = QIcon()
        icon.addPixmap(QPixmap(path), QIcon.Normal, QIcon.Off)
        self._icons[name] = icon

    def icon(self, name):
        icon = self._icons["default"]
        if name not in self._icons:
            file_name = "icons/" + name + ".png"
            try:
                self.make_icon(name, file_name)
            except IOError:
                print("file " + file_name + " not found")
        try:
            icon = self._icons[name]
        except KeyError:
            print("icon " + name + " not found")
        return icon
