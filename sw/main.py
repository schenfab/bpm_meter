import time
import micropython

from led_display import LedDisplay
from machine import Pin

led = LedDisplay()

led.print("888")
led.points(0b111)

time.sleep(1)

led.print("---")
led.points(0b000)

micropython.alloc_emergency_exception_buf(100)

#beat = Pin(24, Pin.IN) # optocoupler
beat = Pin(25, Pin.IN) # MOSFET
#beat = Pin(26, Pin.IN) # ADC

last = -1
def display_bpm(curr):
  global ready, last
  if last > 0:
    period = time.ticks_diff(curr, last)
    bpm = int(60_000 / period + 0.5)
    led.print(bpm)
  last = curr
  ready = 1

def handler(pin):
  global ready
  if ready == 1:
    ready = 0
    micropython.schedule(display_bpm, time.ticks_ms())

ready = 1
beat.irq(handler, Pin.IRQ_RISING | Pin.IRQ_FALLING)
