import machine


scl_pin_id = 5
sda_pin_id = 4
freq = 400000

i2c = machine.I2C(scl = machine.Pin(scl_pin_id, machine.Pin.OUT),
                  sda = machine.Pin(sda_pin_id),
                  freq = freq)

print(i2c.scan())




def read(reg_address):
    return i2c.readfrom_mem(96, reg_address, 1)
    # i2c.writeto(96, bytearray([reg_address]))
    # return i2c.readfrom(96, 1)



def write(reg_address, data):
    return i2c.writeto_mem(96, reg_address, bytearray([data]))
    # return i2c.writeto(96, bytearray([reg_address, data]))


print(write(3, 0xF2))

print(read(3))

# for i in range(128):
#     try:
#         i2c.write_byte(i, 0)
#         print(i)
#     except Exception as e:
#         print(e)
#         pass
