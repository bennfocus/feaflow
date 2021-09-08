class FeaflowException(Exception):
    pass


class NotAllowedException(FeaflowException):
    def __init__(self, msg):
        super().__init__(msg)


class ConfigLoadException(FeaflowException):
    def __init__(self, config_path: str):
        super().__init__(f"Could not load config file '{config_path}`")


class EngineImportException(Exception):
    def __init__(self, engine_config_class_name: str):
        super().__init__(f"Can not import engine config '{engine_config_class_name}'")
