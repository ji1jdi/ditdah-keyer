from keyer import Keyer

class ManualKeyer(Keyer):
    def __init__(self, emitter):
        super().__init__(Keyer.MANUAL)

        self._emitter = emitter

    def handler(self, dit_on, dah_on):
        if dit_on or dah_on:
            self._emitter.emit("on", None)
        else:
            self._emitter.emit("off", None)
