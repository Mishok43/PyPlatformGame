"""Singleton metaclass."""

class Singleton(type):
    """Singleton metaclass.

    :param _instances: dict with instances of classes.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """Singleton call with cached instance.

        :return: DerivedClass singleton instance.
        """
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
