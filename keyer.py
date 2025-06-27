class Keyer:
    IAMBIC = 0
    MANUAL = 1

    NUM_KEYERS = 2

    def __init__(self, type):
        self._type = type
        self._wpm = 20
        self._duration = 1200 / self._wpm

    def handler(self, dit_on, dah_on):
        pass

    @property
    def type(self):
        return self._type

    @property
    def wpm(self):
        return self._wpm

    @wpm.setter
    def wpm(self, value):
        self._wpm = value
        self._duration = 1200 / self._wpm
