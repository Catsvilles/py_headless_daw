from py_headless_daw.project.content.clip import Clip


class AudioClip(Clip):
    def __init__(self, start_time: float, end_time: float, source_file: str, cue_sample: int, rate: float):
        super().__init__(start_time, end_time)
        self.source_file: str = source_file
        self.cue_sample: int = cue_sample
        self.rate: float = rate
