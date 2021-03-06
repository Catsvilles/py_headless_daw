from typing import List

import numpy as np

from py_headless_daw.schema.dto.time_interval import TimeInterval
from py_headless_daw.schema.events.event import Event
from py_headless_daw.schema.events.parameter_value_event import ParameterValueEvent
from py_headless_daw.schema.processing_strategy import ProcessingStrategy


class StreamGain(ProcessingStrategy):
    PARAMETER_GAIN: str = 'gain'

    # noinspection PyShadowingNames
    def render(self, interval: TimeInterval, stream_inputs: List[np.ndarray], stream_outputs: List[np.ndarray],
               event_inputs: List[List[Event]], event_outputs: List[List[Event]]):

        # simplified approach:
        # we check all events arrived and react on any param value events,
        # the last one we face will determine current gain value, if non have arrived,
        # the gain will not change
        all_events = self._flatten_event_inputs(event_inputs)
        all_events = sorted(all_events, key=lambda event: event.sample_position)

        for event in all_events:
            if event.type == Event.TYPE_PARAMETER_VALUE:
                # noinspection PyTypeChecker
                param_value_event: ParameterValueEvent = event
                if param_value_event.parameter_id == self.PARAMETER_GAIN:
                    self.gain = param_value_event.value

        for i in range(0, len(stream_inputs)):
            np.copyto(stream_outputs[i], stream_inputs[i])
            stream_outputs[i] *= self.gain

    def __init__(self, gain: np.float32):
        super().__init__()
        self.gain: np.float32 = gain
