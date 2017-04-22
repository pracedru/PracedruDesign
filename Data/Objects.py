import uuid

__author__ = 'mamj'


class IdObject(object):
    def __init__(self):
        uid = uuid.uuid1().urn[9:]
        self._uid = uid

    @property
    def uid(self):
        return self._uid

    def serialize_json(self):
        return {'uid': self._uid }

    def deserialize_data(self, data):
        self._uid = data['uid']


class ObservableObject(object):
    def __init__(self):
        self._change_handlers = set()
        self._is_modified = False

    def changed(self, event):
        self._is_modified = True
        for handler in list(self._change_handlers):
            handler(event)

    def is_modified(self):
        return self._is_modified

    def set_modified(self, value):
        self._is_modified = value

    def add_change_handler(self, change_handler):
        self._change_handlers.add(change_handler)

    def remove_change_handler(self, change_handler):
        try:
            self._change_handlers.remove(change_handler)
        except KeyError:
            pass
