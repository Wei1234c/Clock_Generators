from clock_generators.si535x.si5351 import Si5351
from utilities.adapters import peripherals


with_hardware_device = False

if with_hardware_device:
    _i2c = peripherals.I2C.get_Ftdi_i2c()

else:
    _i2c = None  # using None for testing without actual hardware device.

si = Si5351(_i2c)

for c in si.clocks:
    print(c.enabled, c.power_downed)

for c in si.clocks:
     c.enable(False), c.power_down(True)

for c in si.clocks:
    print(c.enabled, c.power_downed)

clk = si.clocks[0]
ms = si.multisynthes[0]
pll = si.plls[0]

clk.set_frequency(40e6)
si.plls[0].set_frequency(600e6)

print(clk.freq)
