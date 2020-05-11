try:
    from utilities.adapters.peripherals import I2C
except:
    from peripherals import I2C



class Si5351_proxy:
    I2C_ADDRESS = 0x60
    N_REGISTERS = 188
    OUTPUT_ENABLE_CONTROL_ADDRESS = 3


    def __init__(self, bus, i2c_address = I2C_ADDRESS, registers_values = None):

        self._bus = bus
        self._i2c_address = i2c_address

        self.enable(False)

        if registers_values is not None:
            self.write_all_registers(registers_values)

        self.reset_plls()

        self.enable(True)


    def reset_plls(self):
        self.write_register(177, 0xa0)


    def enable(self, value = True):
        self.write_register(self.OUTPUT_ENABLE_CONTROL_ADDRESS, 0x00 if value else 0xFF)


    def read_register(self, reg_address):
        return self._bus.read_byte(self._i2c_address, reg_address)


    def write_register(self, reg_address, value):
        return self._bus.write_byte(self._i2c_address, reg_address, value)


    def read_all_registers(self):
        addressed_values = []
        for address in range(self.N_REGISTERS):
            try:
                value = self.read_register(address)
                addressed_values.append((address, value))
            except:
                pass
        return addressed_values


    def write_all_registers(self, addressed_values):
        for (address, value) in addressed_values:
            try:
                self.write_register(address, value)
            except:
                pass
