import time
import micropython

from led_display import LedDisplay
from machine import Pin

micropython.alloc_emergency_exception_buf(100)


class BeatHandler:
    def __init__(self, display):
        self._last_beat_ms = 10e9
        self._display = display

    def _update_bpm(self, beat_period_ms):
        tempo_bpm = int(60_000 / beat_period_ms + 0.5)
        self._display.points(0b001)
        self._display.print(tempo_bpm)
        self._display.points(0b000)

    def _irq(self, pin):
        now_ms = time.ticks_ms()
        beat_period_ms = time.ticks_diff(now_ms, self._last_beat_ms)
        self._last_beat_ms = now_ms
        if beat_period_ms > 100:
            micropython.schedule(self._update_bpm, beat_period_ms)

    def start(self, beat_pin):
        beat_pin.irq(self._irq, Pin.IRQ_RISING)


# Define display, beat handler, and beat pin
display = LedDisplay(pwm=0x40)
beat_handler = BeatHandler(display)
beat_pin = Pin(24, Pin.IN, Pin.PULL_UP)  # optocoupler
# beat_pin = Pin(25, Pin.IN) # MOSFET
# beat_pin = Pin(26, Pin.IN) # ADC

# Display test pattern for 1 second
display.print("888")
display.points(0b111)
time.sleep(1)

# Display idle pattern
display.print("---")
display.points(0b000)

# Start measuring
beat_handler.start(beat_pin)
