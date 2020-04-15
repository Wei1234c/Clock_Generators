#  Failed ! _get_registers_map is too big to fit in ESP32

from peripherals import I2C
from si535x import Si535x
from registers_map import _get_registers_map


with_hardware_device = False

if with_hardware_device:
    _i2c = I2C.get_uPy_i2c(id = -1, scl_pin_id = 5, sda_pin_id = 4, freq = 400000)
else:
    _i2c = None  # using None for testing without actual hardware device.

si = Si535x(_i2c)
