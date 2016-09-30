def static(**kwargs):
    def wrapper(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return wrapper
