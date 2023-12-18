from typing import Dict, Any

class SingletonCalledBeforeDefinedError(Exception):
    def __init__(self, message='''
    It seems the singleton instance has not been defined, this must be due to it being called before intended
    i.e. where you only intended to access the already defined instance, you have instantiated it instead.
    '''):
        super().__init__(message)

class SingletonMeta(type):
    """
    NOTE: from refactoring-guru
    """
    _instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]