from collections import defaultdict


class WillowRegistry(object):
    _registered_state_classes = set()
    _registered_operations = defaultdict(dict)
    _registered_converters = dict()
    _registered_image_formats = {}

    def register_operation(self, state_class, operation_name, func):
        self._registered_operations[state_class][operation_name] = func

    def register_converter(self, from_state_class, to_state_class, func):
        if isinstance(from_state_class, list):
            for state_class in from_state_class:
                self.register_converter(state_class, to_state_class, func)
            return

        self._registered_converters[from_state_class, to_state_class] = func

    def register_state_class(self, state_class):
        self._registered_state_classes.add(state_class)

        # Find and register operations/converters
        for attr in dir(state_class):
            val = getattr(state_class, attr)
            if hasattr(val, '_willow_operation'):
                self.register_operation(state_class, val.__name__, val)
            elif hasattr(val, '_willow_converter_to'):
                self.register_converter(state_class, val._willow_converter_to, val)
            elif hasattr(val, '_willow_converter_from'):
                self.register_converter(val._willow_converter_from, state_class, val)

    def register_format(self, image_format, initial_state):
        self._registered_image_formats[image_format] = initial_state

    def get_initial_state_class(self, image_format):
        return self._registered_image_formats[image_format]

    def get_operation(self, state_class, operation_name):
        return self._registered_operations[state_class][operation_name]

    def get_converter(self, from_state_class, to_state_class):
        return self._registered_converters[from_state_class, to_state_class]

    def find_state_class(self, with_operation=None, with_converter_from=None):
        state_classes = self._registered_state_classes

        if with_operation is not None:
            state_classes = filter(lambda state: state in self._registered_operations and with_operation in self._registered_operations[state], state_classes)

        if with_converter_from is not None:
            state_classes = filter(lambda state: (with_converter_from, state) in self._registered_converters, state_classes)

        return list(state_classes)[0]


registry = WillowRegistry()
