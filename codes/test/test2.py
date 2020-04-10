from clock_generators.si535x.si5351 import Si5351
from utilities.adapters import peripherals

with_hardware_device = False

if with_hardware_device:
    _i2c = peripherals.I2C.get_Ftdi_i2c()

else:
    _i2c = None  # using None for testing without actual hardware device.

si = Si5351(_i2c)

si.clocks.enable_all_outputs()