import json
import os

import Data
import GUI
from Data.Document import Document
from Data.Paper import Sizes
from Data.Parameters import Parameters
from Data.Sketch import Sketch, Attribute

undo_stacks = {}


def load_document(file_path):
    data = Data.read_json_data_from_disk(file_path)
    doc = Data.Document.Document.deserialize(data)
    doc.path = os.path.dirname(file_path)
    doc.name = os.path.basename(file_path)
    return doc


def new_document():
    doc = Document()
    main_window = GUI.MainWindow.MainWindow(doc)
    main_window.show()


def save_document(doc: Document):
    data = json.dumps(doc, default=Data.complex_handler)
    Data.write_data_to_disk(doc.path + "/" + doc.name, data)
    doc.set_modified(False)
    doc.set_status('Document saved')


def add_parameter(parameters_object: Parameters):
    parameters_object.create_parameter()


def create_add_sketch_to_document(document):
    sketch = Sketch(document.get_parameters(), document)
    document.get_geometries().add_geometry(sketch)
    document.get_geometries().add_child(sketch)
    return sketch


def add_drawing(document, size, name, header, orientation):
    drawing = document.get_drawings().create_drawing(size, name, header, orientation)
    for text_tuple in header.get_texts():
        text = text_tuple[1]
        if type(text) is Attribute:
            drawing.add_field(text.name, text.value)
    return drawing


def delete_items(doc, items):
    for item in items:
        object = item.data
        if object is not None:
            if "delete" in dir(object):
                object.delete()