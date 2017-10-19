from PyQt5.QtCore import QFileInfo
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QSize
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QDialog
from PyQt5.QtWidgets import QDockWidget
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QToolBar

import Business
from Business.DrawingActions import create_default_header
from Data.Document import Document
from Data.Drawings import Drawing
from Data.Parameters import Parameters
from Data.Part import Part, Feature
from Data.Point3d import KeyPoint
from Data.Sketch import Sketch
from GUI import *
from GUI.ActionsStates import ActionStates
from GUI.Icons import get_icon
from GUI.Ribbon.RibbonButton import RibbonButton
from GUI.Ribbon.RibbonTextbox import RibbonTextbox
from GUI.Ribbon.RibbonWidget import RibbonWidget
from GUI.Widgets.GeometryView import GeometryDock
from GUI.Widgets.NewDrawingView import NewDrawingViewWidget
from GUI.Widgets.ParametersWidget import ParametersWidget
from GUI.Widgets.PropertiesView import PropertiesDock
from GUI.Widgets.TreeView import TreeViewDock
from GUI.Widgets.ViewWidget import ViewWidget

main_windows = []


class MainWindow(QMainWindow):
    def __init__(self, document: Document):
        QMainWindow.__init__(self, None)
        main_windows.append(self)
        self._document = document
        self._document.add_status_handler(self.on_status_changed)
        self.setMinimumHeight(800)
        self.setMinimumWidth(1280)
        self.setWindowIcon(get_icon("icon"))
        self._Title = "Pracedru Design"
        self._states = ActionStates()
        # Action initialization
        
        self.new_action = self.add_action("New\nFile", "newicon", "New Document", True, self.on_new_document, QKeySequence.New)
        self.open_action = self.add_action("Open\nFile", "open", "Open file", True, self.on_open_file, QKeySequence.Open)
        self.save_action = self.add_action("Save", "save", "Save these data", True, self.on_save, QKeySequence.Save)
        self.save_as_action = self.add_action("Save\nas", "saveas", "Save these data as ...", True, self.on_save_as, QKeySequence.SaveAs)
        self._zoom_fit_action = self.add_action("Zoom\nfit", "zoomfit", "Zoom to fit contents", True, self.on_zoom_fit)
        self.add_sketch_to_document_action = self.add_action("Add\nSketch", "addsketch", "Add Sketch to the document", True, self.on_add_sketch_to_document)
        self.add_drawing_action = self.add_action("Add\nDrawing", "adddrawing", "Add drawing to the document", True, self.on_add_drawing)
        self.add_part_action = self.add_action("Add\nPart", "addpart", "Add part to the document", True, self.on_add_part)
        self._show_hidden_params_action = self.add_action("Show hidden\nparameters", "hideparams", "Show hidden parameters", True, self.on_show_hidden_parameters, checkable=True)
        self._set_sim_x_action = self.add_action("Set simil.\nx coords", "setsimx", "Set similar x coordinate values", True, self.on_set_sim_x, checkable=True)
        self._set_sim_y_action = self.add_action("Set simil.\ny coords", "setsimy", "Set similar y coordinate values", True, self.on_set_sim_y, checkable=True)
        self._find_all_sim_action = self.add_action("Find all\nsimmilar", "allsim", "find all similar coordinate values and make parameters", True, self.on_find_all_similar)
        self._add_line_action = self.add_action("Add\nline", "addline", "Add line edge to edges", True, self.on_add_line, checkable=True)
        self._add_arc_action = self.add_action("Add\narc", "addarc", "Add arc edge to edges", True, self.on_add_arc)
        self._add_fillet_action = self.add_action("Add\nfillet", "addfillet", "Add fillet edge to existing edges", True, self.on_add_fillet, checkable=True)
        self._add_divide_action = self.add_action("Divide\nedge", "divideline", "Divide edge with keypoint", True, self.on_divide_edge, checkable=True)
        self._add_text_action = self.add_action("Insert\ntext", "addtext", "Insert text in sketch", True, self.on_insert_text, checkable=True)
        self._add_attribute_action = self.add_action("Insert\nattribute", "addattribute", "Insert attribute in sketch", True, self.on_insert_attribute, checkable=True)
        self._add_circle_action = self.add_action("Insert\ncircle", "addcircle", "Insert circle in sketch", True, self.on_add_circle, checkable=True)
        self._add_nurbs_action = self.add_action("Insert\nspline", "addnurbs", "Insert spline in sketch", True, self.on_add_nurbs, checkable=True)
        self._create_sketch_action = self.add_action("Create\nSketch", "addsketch", "Create Sketch", True, self.on_create_sketch)
        self._create_areas_action = self.add_action("Create\nAreas", "createareas", "Create areas from existing edges", True, self.on_create_areas)
        self._create_area_action = self.add_action("Create\nArea", "createarea", "Create area from existing edges", True, self.on_create_area, checkable=True)
        self._show_area_names_action = self.add_action("Show area\nNames", "showareanames", "Show area names", True, self.on_show_area_names, checkable=True)
        self._scale_selected_action = self.add_action("Scale", "scale", "Scale selected items", True, self.on_scale_selected)
        self._pattern_selected_action = self.add_action("Pattern", "pattern", "Pattern selected items", True, self.on_pattern_selected)
        self._show_key_points_action = self.add_action("Show key\npoints", "showkeypoints", "Show keypoints as circles", True, self.on_show_key_points, checkable=True)
        self._insert_sketch_in_action = self.add_action("Insert\nsketch", "addsketch", "Insert sketch ", True, self.on_insert_sketch)
        self._insert_sketch_in_drawing_action = self.add_action("Insert\nsketch", "addsketchview", "Insert sketch in drawing", True, self.on_insert_sketch)
        self._insert_part_action = self.add_action("Insert\npart", "addpartview", "Insert part in drawing", True, self.on_insert_part_in_drawing)
        self._insert_dim_annotation = self.add_action("Dim", "insertdimannotation", "Insert dimension annotation in drawing", True, self.on_insert_dim_ann_in_drawing)
        self._add_revolve_action = self.add_action("Revolve\nArea", "addrevolve", "Revolve an area on this part", True, self.on_revolve_area)
        self._add_extrude_action = self.add_action("Extrude\nArea", "addextrude", "Extrude an area on this part", True, self.on_extrude_area)
        self._add_nurbs_surface_action = self.add_action("Create\nNurbs Srf.", "nurbssurf", "Create nurbs surface", True, self.on_create_nurbs_surface)
        self._show_surfs_action = self.add_action("Show\nSurfs", "showsurfs", "Show surfaces", True, self.on_show_surfs, checkable=True)
        self._show_lines_action = self.add_action("Show\nLines", "showlines", "Show Lines", True, self.on_show_lines, checkable=True)
        self._show_planes_action = self.add_action("Show\nPlanes", "showplanes", "Show Planes", True, self.on_show_planes, checkable=True)
        self._add_field_action = self.add_action("Insert\nfield", "addfield", "Insert field on drawing", True, self.on_add_field)
        self._about_action = self.add_action("About", "about", "About this programme", True, self.on_about)
        self._write_language_action = self.add_action("Write\nlang", "writelang", "Write language translation file", True, self.on_write_lang)

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


        # Views
        self._treeViewDock = TreeViewDock(self, self._document)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._treeViewDock)
        self._viewWidget = ViewWidget(self, self._document)
        self.setCentralWidget(self._viewWidget)
        self._parameters_dock_widget = QDockWidget(self)
        self._parameters_dock_widget.setObjectName("paramsDock")
        self.parameters_widget = ParametersWidget(self, self._document)
        self._parameters_dock_widget.setWidget(self.parameters_widget)
        self._parameters_dock_widget.setWindowTitle(tr("Parameters"))
        self.addDockWidget(Qt.LeftDockWidgetArea, self._parameters_dock_widget)
        self._geometry_dock = GeometryDock(self, self._document)
        self.addDockWidget(Qt.LeftDockWidgetArea, self._geometry_dock)
        self._properties_dock = PropertiesDock(self, document)
        self.addDockWidget(Qt.RightDockWidgetArea, self._properties_dock)
        self.read_settings()
        self.statusBar().showMessage("Ready")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(20)
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setTextVisible(False)
        self.statusBar().addPermanentWidget(self.progress_bar, 0)
        self.setWindowTitle("{s[0]} - {s[1]}".format(s=[self._document.name, self._Title]))
        self.update_ribbon_state()

    def get_states(self) -> ActionStates:
        return self._states

    def on_new_document(self):
        Business.new_document()

    def on_open_file(self):
        docs_location = QStandardPaths.standardLocations(QStandardPaths.DocumentsLocation)

        default_path = docs_location[0]
        file_name = QFileDialog.getOpenFileName(self, 'Open file', default_path, "Text files (*.jadoc)")
        file_path = file_name[0]

        if file_path != "":
            doc = Business.load_document(file_path)
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

    def on_insert_sketch(self):
        self._viewWidget.on_insert_sketch()

    def on_insert_part_in_drawing(self):
        self._viewWidget.drawing_view.on_insert_part()

    def on_insert_dim_ann_in_drawing(self):
        pass

    def on_revolve_area(self):
        self._viewWidget.part_view.on_revolve_area()

    def on_extrude_area(self):
        self._viewWidget.part_view.on_insert_extrude()

    def on_create_nurbs_surface(self):
        self._viewWidget.part_view.on_create_nurbs_surface()

    def on_show_surfs(self):
        self._viewWidget.part_view.show_surfaces = self._show_surfs_action.isChecked()

    def on_show_lines(self):
        self._viewWidget.part_view.show_lines = self._show_lines_action.isChecked()

    def on_show_planes(self):
        self._viewWidget.part_view.show_planes = self._show_planes_action.isChecked()

    def on_add_field(self):
        self._viewWidget.drawing_view.on_add_field()

    def on_about(self):
        pass

    def on_write_lang(self):
        write_language_file()

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

    def on_add_sketch_to_document(self):
        Business.create_add_sketch_to_document(self._document)

    def on_create_sketch(self):
        self._viewWidget.on_create_sketch()

    def on_tree_selection_changed(self, selection):
        if len(selection) == 1:
            if type(selection[0]) is Sketch:
                self._viewWidget.set_sketch_view(selection[0])
                self._geometry_dock.set_sketch(selection[0])
                self._ribbon_widget.setCurrentIndex(1)
            if type(selection[0]) is Drawing:
                self._viewWidget.set_drawing_view(selection[0])
                self._ribbon_widget.setCurrentIndex(3)
            if isinstance(selection[0], Parameters):
                self.parameters_widget.set_parameters(selection[0])
            if type(selection[0]) is KeyPoint:
                self._viewWidget.on_kp_selection_changed_in_table(selection)
            if type(selection[0]) is Part:
                self._viewWidget.set_part_view(selection[0])
                self._ribbon_widget.setCurrentIndex(2)
            if type(selection[0]) is Feature:
                if selection[0].feature_type == Feature.SketchFeature:
                    sketch = selection[0].get_objects()[0]
                    self._viewWidget.set_sketch_view(sketch)
                    self._geometry_dock.set_sketch(sketch)
                    self._ribbon_widget.setCurrentIndex(1)
                    self.parameters_widget.set_parameters(sketch)
            self._properties_dock.set_item(selection[0])

    def on_kp_selection_changed_in_table(self, selected_key_points):
        self._viewWidget.on_kp_selection_changed_in_table(selected_key_points)

    def on_edge_selection_changed_in_table(self, selected_edges):
        self._viewWidget.on_edge_selection_changed_in_table(selected_edges)

    def on_edge_selection_changed_in_view(self, selected_edges):
        self._geometry_dock.on_edge_selection_changed(selected_edges)
        if len(selected_edges) > 0:
            self._properties_dock.set_item(selected_edges[0])

    def on_kp_selection_changed_in_view(self, selected_key_points):
        self._geometry_dock.on_kp_selection_changed(selected_key_points)
        if len(selected_key_points) > 0:
            self._properties_dock.set_item(selected_key_points[0])

    def on_text_selection_changed_in_view(self, selected_texts):
        if len(selected_texts) > 0:
            self._properties_dock.set_item(selected_texts[0])

    def on_new_item_added_in_tree(self, item_object):
        self._properties_dock.set_item(item_object)

    def on_set_sim_x(self):
        self._viewWidget.on_set_similar_x_coordinates()

    def on_set_sim_y(self):
        self._viewWidget.on_set_similar_y_coordinates()

    def on_add_line(self):
        self._viewWidget.on_add_line()

    def on_add_fillet(self):
        self._viewWidget.on_add_fillet()

    def on_insert_text(self):
        self._viewWidget.on_insert_text()

    def on_insert_attribute(self):
        self._viewWidget.on_insert_attribute()

    def on_add_circle(self):
        self._viewWidget.on_add_circle()

    def on_add_nurbs(self):
        self._viewWidget.on_add_nurbs()

    def on_create_areas(self):
        self._viewWidget.sketch_view.on_create_areas()

    def on_create_area(self):
        self._viewWidget.sketch_view.on_create_area()

    def on_show_area_names(self, event):
        self._states.show_area_names = self._show_area_names_action.isChecked()

    def on_add_arc(self):
        self._viewWidget.sketch_view.on_add_arc()

    def on_divide_edge(self):
        pass

    def on_scale_selected(self):
        pass

    def on_pattern_selected(self):
        pass

    def on_find_all_similar(self):
        self._viewWidget.on_find_all_similar()

    def on_show_key_points(self):
        self._states.show_key_points = self._show_key_points_action.isChecked()
        self._viewWidget.update()

    def on_similar_thresshold_changed(self, event):
        value = float(event)
        self._viewWidget.sketch_view.on_similar_thresshold_changed(value)

    def update_ribbon_state(self):
        self._add_line_action.setChecked(self._states.draw_line_edge)
        self._set_sim_x_action.setChecked(self._states.set_similar_x)
        self._set_sim_y_action.setChecked(self._states.set_similar_y)
        self._add_fillet_action.setChecked(self._states.add_fillet_edge)
        # self._add_arc_action.setEnabled(False)
        self._add_divide_action.setEnabled(False)
        self._scale_selected_action.setEnabled(False)
        self._pattern_selected_action.setEnabled(False)
        self._add_circle_action.setChecked(self._states.add_circle_edge)
        self._add_attribute_action.setChecked(self._states.add_attribute)
        self._add_text_action.setChecked(self._states.add_text)
        self._create_area_action.setChecked(self._states.create_area)
        self._show_surfs_action.setChecked(self._viewWidget.part_view.show_surfaces)
        self._show_lines_action.setChecked(self._viewWidget.part_view.show_lines)
        self._show_planes_action.setChecked(self._viewWidget.part_view.show_planes)
        self._add_nurbs_action.setChecked(self._states.draw_nurbs_edge)

    def init_ribbon(self):
        self.init_home_tab()
        self.init_sketch_tab()
        self.init_part_tab()
        self.init_assembly_tab()
        self.init_drawing_tab()
        self.init_analysis_tab()
        self.init_info_tab()

    def init_home_tab(self):
        home_tab = self._ribbon_widget.add_ribbon_tab("Home")
        file_pane = home_tab.add_ribbon_pane("File")
        file_pane.add_ribbon_widget(RibbonButton(self, self.new_action, True))
        file_pane.add_ribbon_widget(RibbonButton(self, self.open_action, True))
        file_pane.add_ribbon_widget(RibbonButton(self, self.save_action, True))
        file_pane.add_ribbon_widget(RibbonButton(self, self.save_as_action, True))
        insert_pane = home_tab.add_ribbon_pane("Insert")
        insert_pane.add_ribbon_widget(RibbonButton(self, self.add_sketch_to_document_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self.add_part_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self.add_drawing_action, True))

    def init_sketch_tab(self):
        sketch_tab = self._ribbon_widget.add_ribbon_tab("Sketch")
        insert_pane = sketch_tab.add_ribbon_pane("Insert")
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_line_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_nurbs_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_arc_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_circle_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_fillet_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_divide_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_text_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_attribute_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._create_areas_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._create_area_action, True))


        operate_pane = sketch_tab.add_ribbon_pane("Operate")
        operate_pane.add_ribbon_widget(RibbonButton(self, self._scale_selected_action, True))
        operate_pane.add_ribbon_widget(RibbonButton(self, self._pattern_selected_action, True))

        parametry_pane = sketch_tab.add_ribbon_pane("Parametry")
        parametry_pane.add_ribbon_widget(RibbonButton(self, self._set_sim_x_action, True))
        parametry_pane.add_ribbon_widget(RibbonButton(self, self._set_sim_y_action, True))
        parametry_pane.add_ribbon_widget(RibbonButton(self, self._find_all_sim_action, True))
        thresshold_text_box = RibbonTextbox(str(1), self.on_similar_thresshold_changed)
        grid = parametry_pane.add_grid_widget(200)
        grid.addWidget(QLabel("Thresshold"), 0, 0)
        grid.addWidget(thresshold_text_box, 0, 1)


        view_pane = sketch_tab.add_ribbon_pane("View")
        view_pane.add_ribbon_widget(RibbonButton(self, self._show_key_points_action, True))
        view_pane.add_ribbon_widget(RibbonButton(self, self._show_hidden_params_action, True))
        view_pane.add_ribbon_widget(RibbonButton(self, self._zoom_fit_action, True))
        view_pane.add_ribbon_widget(RibbonButton(self, self._show_area_names_action, True))
        sketch_tab.add_spacer()

    def init_part_tab(self):
        part_tab = self._ribbon_widget.add_ribbon_tab(tr("Part"))
        insert_pane = part_tab.add_ribbon_pane(tr("Insert"))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._insert_sketch_in_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._create_sketch_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_extrude_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_revolve_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._add_nurbs_surface_action, True))
        view_pane = part_tab.add_ribbon_pane("View")
        view_pane.add_ribbon_widget(RibbonButton(self, self._show_surfs_action, True))
        view_pane.add_ribbon_widget(RibbonButton(self, self._show_lines_action, True))
        view_pane.add_ribbon_widget(RibbonButton(self, self._show_planes_action, True))

    def init_assembly_tab(self):
        pass

    def init_drawing_tab(self):
        drawing_tab = self._ribbon_widget.add_ribbon_tab("Drawing")
        insert_pane = drawing_tab.add_ribbon_pane("Insert")
        insert_pane.add_ribbon_widget(RibbonButton(self, self._insert_sketch_in_drawing_action, True))
        insert_pane.add_ribbon_widget(RibbonButton(self, self._insert_part_action, True))
        annotation_pane = drawing_tab.add_ribbon_pane("Annotation")
        annotation_pane.add_ribbon_widget(RibbonButton(self, self._insert_dim_annotation, True))
        edit_pane = drawing_tab.add_ribbon_pane("Edit")
        edit_pane.add_ribbon_widget(RibbonButton(self, self._add_field_action, True))
        view_pane = drawing_tab.add_ribbon_pane("View")
        view_pane.add_ribbon_widget(RibbonButton(self, self._zoom_fit_action, True))

    def init_analysis_tab(self):
        pass

    def init_info_tab(self):
        drawing_tab = self._ribbon_widget.add_ribbon_tab("Info")
        information_pane = drawing_tab.add_ribbon_pane("Information")
        information_pane.add_ribbon_widget(RibbonButton(self, self._about_action, True))
        information_pane.add_ribbon_widget(RibbonButton(self, self._write_language_action, True))

    def on_show_hidden_parameters(self):
        pass

    def on_zoom_fit(self):
        self._viewWidget.on_zoom_fit()

    def on_add_drawing(self):
        if len(self._document.get_drawings().get_headers()) == 0:
            create_default_header(self._document)
        new_dwg_widget = NewDrawingViewWidget(self, self._document)
        result = new_dwg_widget.exec_()
        if result == QDialog.Accepted:
            header = new_dwg_widget.header
            size = new_dwg_widget.size
            name = new_dwg_widget.name
            orientation = new_dwg_widget.orientation
            Business.add_drawing(self._document, size, name, header, orientation)

    def on_add_part(self):
        Business.add_part(self._document)

    def add_action(self, caption, icon_name, status_tip, icon_visible, connection, shortcut=None, checkable=False):
        action = QAction(get_icon(icon_name), tr(caption, "ribbon"), self)
        action.setStatusTip(tr(status_tip, "ribbon"))
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
            msg = tr("The document has been modified.\nDo you want to save your changes?")
            ret = QMessageBox.warning(self, tr("Application"), msg, QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
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

    def on_status_changed(self, text, progress):
        # print(text + " " + str(progress))
        self.statusBar().showMessage(text)
        self.progress_bar.setValue(progress)
