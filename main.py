import _thread
import settings
import ssd1306
from machine import Pin, PWM, ADC, I2C
from time import sleep_ms, ticks_ms, ticks_diff
from keyer import Keyer
from iambic_keyer import IambicKeyer
from manual_keyer import ManualKeyer
from keyout import KeyOut
from emitter import Emitter
from buzzer import Buzzer
from moving_average import MovingAverage

dit_pin = Pin(settings.DIT_PIN, Pin.IN, Pin.PULL_UP)
dah_pin = Pin(settings.DAH_PIN, Pin.IN, Pin.PULL_UP)

key_type_pin = Pin(settings.KEY_TYPE_PIN, Pin.IN, Pin.PULL_UP)

keyout = KeyOut(Pin(settings.KEYOUT_PIN, Pin.OUT))

buzzer = Buzzer(PWM(Pin(settings.BUZZER_PIN)))
buzzer.frequency = settings.PITCH_DEFAULT

emitter = Emitter()
emitter.on("on", buzzer.on)
emitter.on("off", buzzer.off)
emitter.on("on", keyout.on)
emitter.on("off", keyout.off)

iambic_keyer = IambicKeyer(emitter)
iambic_keyer.wpm = settings.WPM_DEFAULT

manual_keyer = ManualKeyer(emitter)

keyer_list = [iambic_keyer, manual_keyer]
keyer = iambic_keyer

pitch_pin = ADC(settings.PITCH_PIN)
wpm_pin   = ADC(settings.WPM_PIN)

pitch_avg = MovingAverage(settings.MOVING_AVERAGE_SIZE)
wpm_avg   = MovingAverage(settings.MOVING_AVERAGE_SIZE)

i2c = I2C(0, sda=Pin(settings.OLED_SDA_PIN), scl=Pin(settings.OLED_SCL_PIN))
oled = ssd1306.SSD1306_I2C(settings.OLED_WIDTH, settings.OLED_HEIGHT, i2c)

def setup():
    setup_adc()
    setup_keyer(key_type_pin)

def setup_adc():
    for i in range(settings.MOVING_AVERAGE_SIZE):
        n = pitch_pin.read_u16()
        pitch_avg.update(n)

        n = wpm_pin.read_u16()
        wpm_avg.update(n)

        sleep_ms(1)

def setup_keyer(pin):
    keyer_type = Keyer.IAMBIC
    last_update = 0

    def handler(pin):
        global keyer
        nonlocal keyer_type, last_update

        now = ticks_ms()
        if ticks_diff(now, last_update) > 200:
            keyer_type = (keyer_type + 1) % Keyer.NUM_KEYERS
        last_update = now
        print(keyer_type)

        keyer = keyer_list[keyer_type]

    pin.irq(trigger=Pin.IRQ_FALLING, handler=handler)

def display(oled, keyer_type, pitch, wpm):
    keyer = "Iambic key" if keyer_type == Keyer.IAMBIC else "Manual key"
    speed = "-" if keyer_type == Keyer.MANUAL else wpm

    oled.fill(0)
    oled.text("DitDah Keyer", 0, 0)
    oled.text(f"{keyer}", 0, 16)
    oled.text(f"{pitch}Hz {speed}WPM", 0, 32)
    oled.show()

    print(keyer, pitch, wpm)


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

def ui_thread():
    while True:
        buzzer.frequency = read_pitch()
        keyer.wpm = read_wpm()

        display(oled, keyer.type, buzzer.frequency, keyer.wpm)

        sleep_ms(100)

def loop():
    keyer.handler(not dit_pin.value(), not dah_pin.value())
    sleep_ms(1)

def main():
    setup()

    _thread.start_new_thread(ui_thread, ())

    while True:
        loop()

if __name__ == "__main__":
    main()
