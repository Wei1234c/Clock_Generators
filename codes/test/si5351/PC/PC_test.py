from clock_generators.si535x.si5351 import Si5351
from utilities.adapters import peripherals


with_hardware_device = False

if with_hardware_device:
    _i2c = peripherals.I2C.get_Ftdi_i2c()
else:
    _i2c = None  # using None for testing without actual hardware device.

si = Si5351(_i2c)

clk = si.clocks[0]
ms = si.multisynths[0]
pll = si.plls[0]

si.init()
si.enable(False)
clk.enable(True)
clk.set_frequency(50.4e6)
clk.set_frequency(225e6)
clk.set_frequency(5.2e6)
print(clk.freq)
