from py_headless_daw.schema.events.event import Event


class ParameterValueEvent(Event):

    @property
    def type(self) -> str:
        return Event.TYPE_PARAMETER_VALUE

    def __init__(self, sample_position: int, parameter_id: str, value: float):
        super().__init__(sample_position)
        self.parameter_id: str = parameter_id
        self.value: float = value
