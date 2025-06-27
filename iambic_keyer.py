from keyer import Keyer
from time import ticks_ms

STATE_INIT      = 0
STATE_DIT       = 1
STATE_DAH       = 2
STATE_DIT_SPACE = 3
STATE_DAH_SPACE = 4

class IambicKeyer(Keyer):
    def __init__(self, emitter):
        super().__init__(Keyer.IAMBIC)

        self._emitter = emitter
        self._dit_mem_on = False
        self._dah_mem_on = False
        self._state = STATE_INIT
        self._t0 = 0
        self._t1 = 0
        self._wpm = 20
        self._duration = 1200 / self._wpm

    def handler(self, dit_on, dah_on):
        if dit_on:
            self._dit_mem_on = dit_on
        if dah_on:
            self._dah_mem_on = dah_on

        if ticks_ms() < self._t1:
            return

        self.next_state(dit_on, dah_on)
        self.action()

    def next_state(self, dit_on, dah_on):
        if self._state == STATE_INIT:
            if dit_on:
                self._state = STATE_DIT
            elif dah_on:
                self._state = STATE_DAH
        elif self._state == STATE_DAH_SPACE:
            self._state = STATE_DIT if self._dit_mem_on else STATE_INIT
            self._dit_mem_on = False
            self._dah_mem_on = False
        elif self._state == STATE_DIT_SPACE:
            self._state = STATE_DAH if self._dah_mem_on else STATE_INIT
            self._dit_mem_on = False
            self._dah_mem_on = False
        elif self._state == STATE_DIT:
            self._state = STATE_DIT_SPACE
        elif self._state == STATE_DAH:
            self._state = STATE_DAH_SPACE
        elif self._state == STATE_DIT_SPACE:
            self._state = STATE_INIT
        elif self._state == STATE_DAH_SPACE:
            self._state = STATE_INIT

    def action(self):
        d = 0

        if self._state == STATE_DIT:
            self._emitter.emit("on", None)
            d = self._duration
        elif self._state == STATE_DAH:
            self._emitter.emit("on", None)
            d = self._duration * 3
        elif self._state == STATE_DIT_SPACE or self._state == STATE_DAH_SPACE:
            self._emitter.emit("off", None)
            d = self._duration

        self._t0 = ticks_ms()
        self._t1 = self._t0 + d
