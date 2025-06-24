import settings
from machine import Pin, PWM, ADC
from time import sleep_ms
from keyer import Keyer
from keyout import KeyOut
from emitter import Emitter
from buzzer import Buzzer
from moving_average import MovingAverage

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

pitch_pin = ADC(settings.PITCH_PIN)
wpm_pin   = ADC(settings.WPM_PIN)

pitch_avg = MovingAverage(settings.MOVING_AVERAGE_SIZE)
wpm_avg   = MovingAverage(settings.MOVING_AVERAGE_SIZE)

def setup():
    setup_adc()

def setup_adc():
    for i in range(settings.MOVING_AVERAGE_SIZE):
        n = pitch_pin.read_u16()
        pitch_avg.update(n)

        n = wpm_pin.read_u16()
        wpm_avg.update(n)

        sleep_ms(1)

def linear_scale(x, x_min, x_max, y_min, y_max):
    return round((x - x_min) / (x_max - x_min) * (y_max - y_min) + y_min)

def round_to_step(x, step=5):
    return round(x / step) * step

def read_pitch():
    n = pitch_pin.read_u16()
    pitch_avg.update(n)
    n = linear_scale(pitch_avg.average(), 0, 65535, settings.PITCH_MIN, settings.PITCH_MAX)
    return round_to_step(n, settings.PITCH_STEP)

def read_wpm():
    n = wpm_pin.read_u16()
    wpm_avg.update(n)
    return linear_scale(wpm_avg.average(), 0, 65535, settings.WPM_MIN, settings.WPM_MAX)

def loop(c):
    if c % 100 == 0:
        buzzer.frequency = read_pitch()
        keyer.wpm = read_wpm()
        print(buzzer.frequency, keyer.wpm)

    keyer.handler(not dit_pin.value(), not dah_pin.value())

def main():
    setup()

    c = 0
    while True:
        loop(c)
        c += 1
        sleep_ms(1)

if __name__ == "__main__":
    main()
