from machine import Pin, I2C

led_chars = {
#       A B C D E F G
  "0": [1,1,1,1,1,1,0],
  "1": [0,1,1,0,0,0,0],
  "2": [1,1,0,1,1,0,1],
  "3": [1,1,1,1,0,0,1],
  "4": [0,1,1,0,0,1,1],
  "5": [1,0,1,1,0,1,1],
  "6": [1,0,1,1,1,1,1],
  "7": [1,1,1,0,0,0,0],
  "8": [1,1,1,1,1,1,1],
  "9": [1,1,1,1,0,1,1],
  " ": [0,0,0,0,0,0,0],
  "-": [0,0,0,0,0,0,1],
}

led_pins = [
#   A  B  C  D  E  F  G DP
  [20,19,17,16,15,21,22,18],
  [24,23,13,12,11,25,26,14],
  [28,27, 9, 8, 7,29,30,10],
]

def led_init():
  sdb=Pin(2, Pin.OUT)
  sdb.off()

  global i2c
  i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)

  for i in range(0x26, 0x49):
    i2c.writeto_mem(60, i, b'\x00')  # Disable all outputs
  for i in range(0x07, 0x1E):
    i2c.writeto_mem(60, i, b'\x40')  # Set PWM for all outputs
  i2c.writeto_mem(60, 0x25, b'\x00') # Update all output registers
  i2c.writeto_mem(60, 0x00, b'\x01') # Enable normal operation

  sdb.on()

def led_output(pin, value):
  i2c.writeto_mem(60, 0x26+pin-1, str(value).encode())

def led_print_char(pos, char):
  for i in range(7):
    led_output(led_pins[pos][i], led_chars[char][i])
  i2c.writeto_mem(60, 0x25, b'\x00') # Update all output registers

def led_print(value):
  padded_str="   "+str(value)
  for pos in range(3):
    led_print_char(pos, padded_str[-1-pos])

led_init()
for i in range(1000):
  led_print(i)
for i in range(1000):
  led_print(999-i)
