class Model(object):
    entity_id = int

    @classmethod
    def __get_attribute(cls, path):
        return reduce(lambda obj, attr: getattr(obj, attr, None), path.split('.'), cls)

    @classmethod
    def __get_class_vars(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(key)}

    @classmethod
    def insert(cls):
        pass

    @classmethod
    def select(cls):
        pass

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls):
        pass
