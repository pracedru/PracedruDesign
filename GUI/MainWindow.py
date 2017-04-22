from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QToolBar

import Business
from GUI import *
from GUI.Icons import get_icon
from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.Ribbon.RibbonWidget import RibbonWidget
from GUI.Widgets.ParametersWidget import ParametersWidget
from GUI.Widgets.TreeView import TreeViewDock
from GUI.Widgets.ViewWidget import ViewWidget


class MainWindow(QMainWindow):
    def __init__(self, document):
        QMainWindow.__init__(self, None)
        self._document = document
        self.setMinimumHeight(800)
        self.setMinimumWidth(1280)
        self._Title = "Pracedru Design"
        # Action initialization

        self.new_action = self.add_action("New\nFile", "newicon", "New Document", True, self.on_new_document, QKeySequence.New)
        self.open_action = self.add_action("Open\nFile", "open", "Open file", True, self.on_open_file, QKeySequence.Open)
        self.save_action = self.add_action("Save", "save", "Save these data", True, self.on_save, QKeySequence.Save)
        self.save_as_action = self.add_action("Save\nas", "saveas", "Save these data as ...", True, self.on_save_as, QKeySequence.SaveAs)

        # Ribbon initialization
        self._ribbon = QToolBar(self)
        if is_dark_theme():
            self._ribbon.setStyleSheet(get_stylesheet("ribbon_dark"))
        else:
            self._ribbon.setStyleSheet(get_stylesheet("ribbon"))
        self._ribbon.setObjectName("ribbonWidget")
        self._ribbon.setWindowTitle("Ribbon")
        self.addToolBar(self._ribbon)
        self._ribbon.setMovable(False)
        self._ribbon_widget = RibbonWidget(self)
        self._ribbon_widget.currentChanged.connect(self.on_ribbon_changed)
        self._ribbon.addWidget(self._ribbon_widget)
        self.init_ribbon()
        self.update_ribbon_state()

        # Views

        self._treeViewDock = TreeViewDock(self, self._document)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._treeViewDock)

        self._viewWidget = ViewWidget(self, self._document)
        self.setCentralWidget(self._viewWidget)

        self._parameters_dock_widget = QDockWidget(self)
        self._parameters_dock_widget.setObjectName("paramsDock")
        self.parameters_widget = ParametersWidget(self, self._document)
        self._parameters_dock_widget.setWidget(self.parameters_widget)
        self._parameters_dock_widget.setWindowTitle("Parameters")
        self.addDockWidget(Qt.LeftDockWidgetArea, self._parameters_dock_widget)

        self.read_settings()


    def on_new_document(self):
        Business.new_document()

    def on_open_file(self):
        docs_location = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)

        default_path = docs_location[0]
        file_name = QFileDialog.getOpenFileName(self, 'Open file', default_path, "Text files (*.jadoc)")
        file_path = file_name[0]

        if file_path != "":
            # doc = load_document(file_path)
            try:
                doc = Business.load_document(file_path)
            except ValueError as e:
                QMessageBox.information(self, "Error on load", "ValueError" + str(e))
                return
            except KeyError as e:
                QMessageBox.information(self, "Error on load", "Key Error" + str(e))
                return
            main_window = MainWindow(doc)
            main_window.show()

            if (self._document.is_modified() is False) and self._document.path == "":
                self.close()
        return

    def on_save(self):
        if self._document.path == "" or self._document.name == "":
            return self.on_save_as()
        else:
            Business.save_document(self._document)
            return True

    def on_save_as(self):
        docs_location = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)
        default_path = docs_location[0]
        file_types = "Text File(*.jadoc)"
        file_name = QFileDialog.getSaveFileName(self, "Save file", default_path, file_types)
        if file_name[0] != "":
            if ".jadoc" in file_name[0]:
                file_info = QFileInfo(file_name[0])
            else:
                file_info = QFileInfo(file_name[0] + ".jadoc")
            self._document.path = file_info.absolutePath()
            self._document.name = file_info.fileName()
            self.setWindowTitle("{s[0]} - {s[1]}".format(s=[self._document.name, self._Title]))
            self.on_save()
            return True
        return False

    def on_ribbon_changed(self):
        pass

    def update_ribbon_state(self):
        pass

    def init_ribbon(self):
        self.init_home_tab()
        self.init_sketch_tab()
        self.init_part_tab()
        self.init_assembly_tab()
        self.init_drawing_tab()
        self.init_analysis_tab()

    def init_home_tab(self):
        home_tab = self._ribbon_widget.add_ribbon_tab("Home")
        file_pane = home_tab.add_ribbon_pane("File")
        file_pane.add_ribbon_widget(RibbonButton(self, self.new_action, True))
        file_pane.add_ribbon_widget(RibbonButton(self, self.open_action, True))
        file_pane.add_ribbon_widget(RibbonButton(self, self.save_action, True))
        file_pane.add_ribbon_widget(RibbonButton(self, self.save_as_action, True))

    def init_sketch_tab(self):
        sketch_tab = self._ribbon_widget.add_ribbon_tab("Sketch")
        insert_pane = sketch_tab.add_ribbon_pane("Insert")
        view_pane = sketch_tab.add_ribbon_pane("View")

    def init_part_tab(self):
        part_tab = self._ribbon_widget.add_ribbon_tab("Part")
        insert_pane = part_tab.add_ribbon_pane("Insert")

    def init_assembly_tab(self):
        pass

    def init_drawing_tab(self):
        pass

    def init_analysis_tab(self):
        pass

    def add_action(self, caption, icon_name, status_tip, icon_visible, connection, shortcut=None, checkable=False):
        action = QAction(get_icon(icon_name), caption, self)
        action.setStatusTip(status_tip)
        action.triggered.connect(connection)
        action.setIconVisibleInMenu(icon_visible)
        if shortcut is not None:
            action.setShortcuts(shortcut)
        action.setCheckable(checkable)
        self.addAction(action)
        return action

    def closeEvent(self, event):
        if self.maybe_save():
            self.write_settings()
            event.accept()
        else:
            event.ignore()

    def maybe_save(self):
        if self._document.is_modified():
            ret = QMessageBox.warning(self, "Application", "The document has been modified.\nDo you want to save your changes?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            if ret == QMessageBox.Save:
                return self.on_save()
            if ret == QMessageBox.Cancel:
                return False
        return True

    def read_settings(self):
        settings = QSettings("PracedruCOM", "PracedruDesign")
        exists = settings.value("exists", False)
        version = int(settings.value("version", 0))
        if not exists or version < 1:
            settings = QSettings("./PracedruDesign.conf", QSettings.IniFormat)
        pos = settings.value("pos", QPoint(100, 100))
        size = settings.value("size", QSize(1280, 800))
        self.resize(size)
        self.move(pos)
        docks_settings_data = settings.value("docks")
        if docks_settings_data is not None:
            self.restoreState(docks_settings_data, 1)
        if settings.value("maximized") == "true":
            self.showMaximized()

    def write_settings(self):
        settings = QSettings("PracedruCOM", "PracedruDesign")
        settings.setValue("exists", True)
        settings.setValue("version", 1)
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        settings.setValue("maximized", self.isMaximized())
        settings.setValue("docks", self.saveState(1))