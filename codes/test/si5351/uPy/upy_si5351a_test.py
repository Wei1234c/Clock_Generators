from peripherals import I2C


with_hardware_device = True

if with_hardware_device:
    _i2c = I2C.get_uPy_i2c(id = -1, scl_pin_id = 5, sda_pin_id = 4, freq = 400000)
else:
    _i2c = None  # using None for testing without actual hardware device.

from si5351a import Si5351A_B_GT


si = Si5351A_B_GT(_i2c)
si.enable(False)

clk = si.clocks[0]
clk.enable(True)
print(clk.status)
