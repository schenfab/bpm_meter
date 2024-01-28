from machine import Pin, I2C


class LedDisplay:
    _ADDR = 60  # I2C address of LED driver (IS31FL3236)

    _REG_SSD = 0x00
    _REG_PWM_BASE = 0x01
    _REG_UPDATE = 0x25
    _REG_CTRL_BASE = 0x26
    _REG_GLOBAL = 0x4A
    _REG_PWM_FREQ = 0x4B
    _REG_RESET = 0x4F

    _OUT_MIN = 7
    _OUT_MAX = 30

    # Segment assignment:
    #         ___
    #        | A |
    #        F   B
    #        |-G-|
    #        E   C
    #        |_D_|
    #
    _CHARS = {
        #     A  B  C  D  E  F  G
        "0": [1, 1, 1, 1, 1, 1, 0],
        "1": [0, 1, 1, 0, 0, 0, 0],
        "2": [1, 1, 0, 1, 1, 0, 1],
        "3": [1, 1, 1, 1, 0, 0, 1],
        "4": [0, 1, 1, 0, 0, 1, 1],
        "5": [1, 0, 1, 1, 0, 1, 1],
        "6": [1, 0, 1, 1, 1, 1, 1],
        "7": [1, 1, 1, 0, 0, 0, 0],
        "8": [1, 1, 1, 1, 1, 1, 1],
        "9": [1, 1, 1, 1, 0, 1, 1],
        " ": [0, 0, 0, 0, 0, 0, 0],
        "-": [0, 0, 0, 0, 0, 0, 1],
    }

    _PINS = [
        # A   B   C   D   E   F   G  DP
        [20, 19, 17, 16, 15, 21, 22, 18],
        [24, 23, 13, 12, 11, 25, 26, 14],
        [28, 27, 9, 8, 7, 29, 30, 10],
    ]

    def __init__(self, pwm=0x40):
        self.i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400_000)
        self.sdb = Pin(2, Pin.OUT)

        self.sdb.off()

        self.i2c.writeto_mem(self._ADDR, self._REG_RESET, b"\x00")
        for i in range(
            self._REG_PWM_BASE + self._OUT_MIN - 1,
            self._REG_PWM_BASE + self._OUT_MAX - 1,
        ):
            self.i2c.writeto_mem(self._ADDR, i, str(pwm).encode())
        self.i2c.writeto_mem(self._ADDR, self._REG_UPDATE, b"\x00")
        self.i2c.writeto_mem(self._ADDR, self._REG_PWM_FREQ, b"\x01")
        self.i2c.writeto_mem(self._ADDR, self._REG_SSD, b"\x01")

        self.sdb.on()

    def _output(self, pin, value):
        self.i2c.writeto_mem(
            self._ADDR, self._REG_CTRL_BASE + pin - 1, str(value).encode()
        )

    def _print_char(self, pos, char):
        for i in range(7):
            self._output(self._PINS[pos][i], self._CHARS[char][i])
        self.i2c.writeto_mem(self._ADDR, self._REG_UPDATE, b"\x00")

    def print(self, value):
        padded_str = "   " + str(value)
        for pos in range(3):
            self._print_char(pos, padded_str[-1 - pos])

    def points(self, value):
        for pos in range(3):
            self._output(self._PINS[pos][-1], value % 2)
            value >>= 1
        self.i2c.writeto_mem(self._ADDR, self._REG_UPDATE, b"\x00")
