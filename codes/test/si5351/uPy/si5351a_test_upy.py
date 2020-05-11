from peripherals import I2C
from si5351a import Si5351A_B_GT


with_hardware_device = True

if with_hardware_device:
    _i2c = I2C.get_uPy_i2c(id = -1, scl_pin_id = 5, sda_pin_id = 4, freq = 400000)
else:
    _i2c = None  # using None for testing without actual hardware device.

bus = I2C(_i2c)
si = Si5351A_B_GT(bus)

si.enable(False)
clk = si.clocks[0]
clk.enable(True)
print(si.multisynths[1].status)
print(clk.status)
