from signal_generators import adapters
from signal_generators.si535x import Si5351

with_hardware_device = True

if with_hardware_device:
    _i2c = adapters.I2C.get_Ftdi_i2c()
else:
    _i2c = None  # using None for testing without actual hardware device.

ad = Si5351(_i2c)
