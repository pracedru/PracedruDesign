#!/usr/bin/python3
import sys

from PyQt5.QtCore import QTranslator, QLocale
from PyQt5.QtWidgets import *

import Business
from Data.Document import Document
from GUI.MainWindow import MainWindow
import os
from pathlib import Path

__author__ = 'mamj'

# This is a test

def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def load_language(a):
    locale = QLocale()    
    translator = QTranslator(a)
    fname = "translate/%s.qm" % locale.name()
    if not os.path.isfile(fname):
        if "_" in locale.name():
            index = locale.name().index('_')
            fname = "translate/%s.qm" % locale.name()[:index]
    if os.path.isfile(fname):
        if translator.load(fname):
            a.installTranslator(translator)


def main():
    a = QApplication(sys.argv)
    a.setQuitOnLastWindowClosed(True)
    load_language(a)
    if len(sys.argv) > 1:
        my_file = Path(sys.argv[1])
        if my_file.is_file():
            document = Business.load_document(sys.argv[1])
        else:
            document = Document()
    else:
        document = Document()
    main_window = MainWindow(document)
    main_window.show()
    sys.exit(a.exec())


sys.excepthook = except_hook
main()
