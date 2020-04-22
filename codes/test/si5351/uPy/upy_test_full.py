#  Failed ! _get_registers_map is too big to fit in ESP32
import gc
gc.collect()

from peripherals import I2C
from si5351 import Si5351A_B_GT
from registers_map import _get_registers_map

with_hardware_device = False

if with_hardware_device:
    _i2c = I2C.get_uPy_i2c(id = -1, scl_pin_id = 5, sda_pin_id = 4, freq = 400000)
else:
    _i2c = None  # using None for testing without actual hardware device.

gc.collect()
si = Si5351A_B_GT(_i2c )# ,registers_map = None)

map = _get_registers_map()