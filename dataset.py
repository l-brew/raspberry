from multiprocessing.sharedctypes import Value
from typing import Dict, List
from threading import Lock


class Dataset:

    class Datapoint:
        def __init__(self, value=None, type=None) -> None:
            self.value = value
            self.type = type
            self.callbacks = []
            self.tags: List[str] = []
            self.changed = True

    def __init__(self) -> None:
        self.datapoints: Dict[str, Dataset.Datapoint] = {}
        self.tag_callbacks: Dict[str, function] = {}
        self.global_callbacks: List[function] = []
        self.lock = Lock()
        pass

    def update(self, name, value, create=False, type_t=None, set_changed=True):
        with self.lock:
            self.__update(name, value, create, type_t, set_changed)

    def __update(self, name, value, create=False, type_t=None, set_changed=True):
        if name not in self.datapoints:
            if create:
                create(name, type_t)
            else:
                raise KeyError("%s does not exist" % name)

        dp = self.datapoints[name]
        if set_changed:
            dp.changed = True
        if dp.type == None or dp.type == type(value):
            dp.value = value
        else:
            raise(TypeError("value must be of type%s", dp.type))

        # call global callbacks
        for f in self.global_callbacks:
            f(name, dp.value)

        # call tag callbacks:
        for t in dp.tags:
            for f in self.tag_callbacks[t]:
                f(name, dp.value)

        # call datapoint callbacks
        for f in dp.callbacks:
            f(name, dp.value)

    def update_if_unchanged(self, name, value,
                            create=False,
                            type_t=None, set_changed=True):
        with self.lock:
            if not self.datapoints[name].changed:
                self.__update(name, value, create, type_t, set_changed)

    def create(self, name, type_t=None):
        with self.lock:
            if name not in self.datapoints:
                self.datapoints[name] = Dataset.Datapoint(type=type_t)

    # return a datapoint value.
    # creates a new one if datapoint dose not exist and create parameter is true
    # if alt is not None and the datapoint dose not exist, alt is retured
    # raises KeyError if datapoint dose not exist, create is False and alt is None
    def get_value(self, name: str, create=False, type_t=None, alt=None):
        with self.lock:
            if name not in self.datapoints:
                if create:
                    self.create(name, type_t)
                    if alt != None:
                        self.datapoints[name].value = alt
                        return alt
                    return None
                if alt != None:
                    return alt
                else:
                    raise KeyError("%s does not exist" % name)
            else:
                return self.datapoints[name].value

    def clear_changed(self, name):
        with self.lock:
            self.datapoints[name].changed = False

    def has_changed(self, name):
        return self.datapoints[name].changed

    def register_tag_callback(self, f, tag: str):
        with self.lock:
            self.tag_callbacks.update({tag: f})

    def register_global_callback(self, f):
        with self.lock:
            self.global_callbacks.append(f)

    def register_datapoint_callback(self, f, name: str):
        with self.lock:
            dp = self.datapoints[name]
            dp.callbacks.append(f)

    def yield_by_tag(self, tag):
        for name, dp in self.datapoints.items():
            if tag in dp.tags:
                yield (name, dp.value)
