from typing import Optional

from py_headless_daw.project.value_provider_consumer import ValueProvider, ValueConsumer


class Parameter(ValueConsumer):
    def __init__(self, name: str, value: float):
        super().__init__()
        self.name: str = name
        self.value: float = value



