from typing import List, cast

import numpy as np

from py_headless_daw.project.content.midi_clip_event import MidiClipEvent
from py_headless_daw.project.content.midi_note import MidiNote
from py_headless_daw.project.midi_track import MidiTrack
from py_headless_daw.schema.dto.time_interval import TimeInterval
from py_headless_daw.schema.events.event import Event
from py_headless_daw.schema.events.midi_event import MidiEvent
from py_headless_daw.schema.events.midi_event_factory import MidiEventFactory
from py_headless_daw.schema.processing_strategy import ProcessingStrategy


class MidiTrackStrategy(ProcessingStrategy):
    def __init__(self, track: MidiTrack):
        super().__init__()
        self.track = track
        self._midi_event_factory: MidiEventFactory = MidiEventFactory()

    def render(self, interval: TimeInterval, stream_inputs: List[np.ndarray], stream_outputs: List[np.ndarray],
               event_inputs: List[List[Event]], event_outputs: List[List[Event]]):

        clip_events: List[MidiClipEvent] = self.track.get_events(interval.start_in_seconds, interval.end_in_seconds)
        midi_events = map(self._clip_event_transformer, clip_events)
        for event_output in event_outputs:
            for midi_event in midi_events:
                event_output.append(midi_event)

    def _clip_event_transformer(self, interval: TimeInterval, clip_event: MidiClipEvent) -> List[MidiEvent]:
        """
        the result can be multiple events

        :param interval:
        :param clip_event:
        :return:
        """
        if isinstance(clip_event, MidiNote):
            midi_note: MidiNote = cast(MidiNote, clip_event)
            return self._convert_midi_note_to_events(interval, midi_note)

    def _convert_midi_note_to_events(self, interval: TimeInterval, midi_note: MidiNote) -> List[MidiEvent]:
        note_start_in_seconds = midi_note.get_absolute_time()
        note_end_in_seconds = midi_note.get_absolute_time_of_note_off()

        if note_start_in_seconds > interval.end_in_seconds:
            raise Exception(
                'note start falls to the right of the interval: ' + str(note_start_in_seconds) + ' > ' + str(
                    interval.end_in_seconds) + '. It should not have happened, must be a bug')

        if note_end_in_seconds < interval.start_in_seconds:
            raise Exception('note ends falls to the left of the interval: ' + str(note_end_in_seconds) + ' < ' + str(
                interval.start_in_seconds) + '. It should not have happened, must be a bug')

        res: List[MidiEvent] = []

        if note_start_in_seconds >= interval.start_in_seconds:
            sample_position = self._calculate_sample_position(interval, note_start_in_seconds)
            res.append(
                self._midi_event_factory.create_note_on_event(midi_note.note, midi_note.velocity, sample_position))

        if note_end_in_seconds <= interval.end_in_seconds:
            sample_position = self._calculate_sample_position(interval, note_end_in_seconds)
            res.append(
                self._midi_event_factory.create_note_off_event(midi_note.note, midi_note.velocity, sample_position))

        return res

    @staticmethod
    def _calculate_sample_position(interval: TimeInterval, event_time_in_seconds: float) -> int:
        assert interval.start_in_seconds <= event_time_in_seconds <= interval.end_in_seconds
        relative_time_in_seconds = event_time_in_seconds - interval.start_in_seconds
        assert 0 <= relative_time_in_seconds <= interval.get_length_in_seconds()

        return round(interval.num_samples * relative_time_in_seconds / interval.get_length_in_seconds())
