import settings
from machine import Pin, PWM
from time import sleep
from keyer import Keyer
from keyout import KeyOut
from emitter import Emitter
from buzzer import Buzzer

dit_pin = Pin(settings.DIT_PIN, Pin.IN, Pin.PULL_UP)
dah_pin = Pin(settings.DAH_PIN, Pin.IN, Pin.PULL_UP)

keyout = KeyOut(Pin(settings.KEYOUT_PIN, Pin.OUT))

buzzer = Buzzer(PWM(Pin(settings.BUZZER_PIN)))
buzzer.frequency = settings.PITCH_DEFAULT

emitter = Emitter()
emitter.on("on", buzzer.on)
emitter.on("off", buzzer.off)
emitter.on("on", keyout.on)
emitter.on("off", keyout.off)

keyer = Keyer(emitter)
keyer.wpm = settings.WPM_DEFAULT

def loop():
    keyer.handler(not dit_pin.value(), not dah_pin.value())

def main():
    while True:
        loop()
        sleep(0.001)

if __name__ == "__main__":
    main()
