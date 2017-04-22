import sys
from PyQt5.QtWidgets import *

import Business
from Data.Document import Document
from GUI.MainWindow import MainWindow
# import Business.ActionHandler
import os
from pathlib import Path

__author__ = 'mamj'
if os.name == "nt":
    os.chdir("P:\SETUP\Topsoe\AnsysPrep")


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def main():
    a = QApplication(sys.argv)
    a.setQuitOnLastWindowClosed(True)

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
