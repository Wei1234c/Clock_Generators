import sys


IS_MICROPYTHON = (sys.implementation.name == 'micropython')

try:
    from utilities.register import RegistersMap
    from .registers_map import _get_all_registers
    # from .registers_map_mini import _get_all_registers
except:
    from register import RegistersMap


    if IS_MICROPYTHON:
        from registers_map_mini import _get_all_registers
    else:
        from registers_map import _get_all_registers



def _get_registers_map():
    raw_registers = _get_all_registers()

    names = [reg.name for reg in raw_registers]
    duplicated_names = list((n for n in set(names) if names.count(n) > 1))

    for reg in raw_registers:
        if reg.name in duplicated_names:
            reg.name = '{}_{}'.format(reg.name, reg.address)

    regs_map = RegistersMap(name = 'Si5351', description = 'Si5351 registers.', registers = raw_registers)

    reg = regs_map.registers['Crystal_Internal_Load_Capacitance']
    reg.elements['Reserved_0'].read_only = False
    reg.default_value = 0xD2
    reg.reset()
    reg.elements['Reserved_0'].read_only = True

    return regs_map
