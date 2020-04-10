# https://www.silabs.com/documents/public/data-sheets/Si5351-B.pdf
# https://www.silabs.com/documents/public/application-notes/AN619.pdf


try:
    from ..interfaces import *
    from utilities.register import RegistersMap, Register, Element, array
    from utilities.adapters.peripherals import I2C
except:
    from interfaces import *
    from register import RegistersMap, Register, Element, array
    from peripherals import I2C



def _get_all_raw_registers():
    registers = []

    registers.append(Register(name = 'Device_Status', address = 0, description = 'Device_Status',
                              elements = [Element(name = 'SYS_INIT', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'System Initialization Status.'),
                                          Element(name = 'LOL_B', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'PLLB Loss Of Lock Status.'),
                                          Element(name = 'LOL_A', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLL A Loss Of Lock Status.'),
                                          Element(name = 'LOS_CLKIN', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'CLKIN Loss Of Signal (Si5351C Only).'),
                                          Element(name = 'LOS_XTAL', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Crystal Loss of Signal'),
                                          Element(name = 'Reserved_2', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          Element(name = 'REVID', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Revision number of the device.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Interrupt_Status_Sticky', address = 1, description = 'Interrupt_Status_Sticky',
                              elements = [Element(name = 'SYS_INIT_STKY', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'System Calibration Status Sticky Bit.'),
                                          Element(name = 'LOL_B_STKY', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'PLLB Loss Of Lock Status Sticky Bit.'),
                                          Element(name = 'LOL_A_STKY', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLLA Loss Of Lock Status Sticky Bit.'),
                                          Element(name = 'LOS_CLKIN_STKY', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'CLKIN Loss Of Signal Sticky Bit (Si5351C Only).'),
                                          Element(name = 'LOS_XTAL_STKY', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Crystal Loss of Signal Sticky Bit'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Interrupt_Status_Mask', address = 2, description = 'Interrupt_Status_Mask',
                              elements = [Element(name = 'SYS_INIT_MASK', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'System Initialization Status Mask.'),
                                          Element(name = 'LOL_B_MASK', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'PLLB Loss Of Lock Status Mask.'),
                                          Element(name = 'LOL_A_MASK', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLL A Loss Of Lock Status Mask.'),
                                          Element(name = 'LOS__CLKIN_MASK', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'CLKIN Loss Of Signal Mask (Si5351C Only).'),
                                          Element(name = 'LOS__XTAL_MASK', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Crystal Loss of Signal Mask'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 3, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Output_Enable_Control', address = 3, description = 'Output_Enable_Control',
                              elements = [Element(name = 'CLK7_OEB', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK7.'),
                                          Element(name = 'CLK6_OEB', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK6.'),
                                          Element(name = 'CLK5_OEB', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK5.'),
                                          Element(name = 'CLK4_OEB', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK4.'),
                                          Element(name = 'CLK3_OEB', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK3.'),
                                          Element(name = 'CLK2_OEB', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK2.'),
                                          Element(name = 'CLK1_OEB', idx_lowest_bit = 1, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK1.'),
                                          Element(name = 'CLK0_OEB', idx_lowest_bit = 0, n_bits = 1, value = 0,
                                                  description = 'Output Disable for CLK0.'),
                                          ], default_value = 0))

    registers.append(
        Register(name = 'OEB_Pin_Enable_Control_Mask', address = 9, description = 'OEB_Pin_Enable_Control_Mask',
                 elements = [Element(name = 'OEB_MAS_K7', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK7.'),
                             Element(name = 'OEB_MAS_K6', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK6.'),
                             Element(name = 'OEB_MAS_K5', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK5.'),
                             Element(name = 'OEB_MAS_K4', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK4.'),
                             Element(name = 'OEB_MAS_K3', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK3.'),
                             Element(name = 'OEB_MAS_K2', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK2.'),
                             Element(name = 'OEB_MAS_K1', idx_lowest_bit = 1, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK1.'),
                             Element(name = 'OEB_MAS_K0', idx_lowest_bit = 0, n_bits = 1, value = 0,
                                     description = 'OEB pin enable control of CLK0.'),
                             ], default_value = 0))

    registers.append(Register(name = 'PLL_Input_Source', address = 15, description = 'PLL_Input_Source',
                              elements = [Element(name = 'CLKIN_DIV', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'ClKIN Input Divider.'),
                                          Element(name = 'Reserved_4', idx_lowest_bit = 4, n_bits = 2, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          Element(name = 'PLLB_SRC', idx_lowest_bit = 3, n_bits = 1, value = 0,
                                                  description = 'Input Source Select for PLLB.'),
                                          Element(name = 'PLLA_SRC', idx_lowest_bit = 2, n_bits = 1, value = 0,
                                                  description = 'Input Source Select for PLLA.'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK0_Control', address = 16, description = 'CLK0_Control',
                              elements = [Element(name = 'CLK0_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 0 Power Down.'),
                                          Element(name = 'MS0_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 0 Integer Mode.'),
                                          Element(name = 'MS0_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK0.'),
                                          Element(name = 'CLK0_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 0 Invert.'),
                                          Element(name = 'CLK0_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 0 Input Source.'),
                                          Element(name = 'CLK0_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK0 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK1_Control', address = 17, description = 'CLK1_Control',
                              elements = [Element(name = 'CLK1_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 1 Power Down.'),
                                          Element(name = 'MS1_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 1 Integer Mode.'),
                                          Element(name = 'MS1_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK1.'),
                                          Element(name = 'CLK1_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 1 Invert.'),
                                          Element(name = 'CLK1_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 1 Input Source.'),
                                          Element(name = 'CLK1_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK1 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK2_Control', address = 18, description = 'CLK2_Control',
                              elements = [Element(name = 'CLK2_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 2 Power Down.'),
                                          Element(name = 'MS2_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 2 Integer Mode.'),
                                          Element(name = 'MS2_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK2.'),
                                          Element(name = 'CLK2_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 2 Invert.'),
                                          Element(name = 'CLK2_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 2 Input Source.'),
                                          Element(name = 'CLK2_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK2 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK3_Control', address = 19, description = 'CLK3_Control',
                              elements = [Element(name = 'CLK3_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 3 Power Down.'),
                                          Element(name = 'MS3_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 3 Integer Mode.'),
                                          Element(name = 'MS3_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK3.'),
                                          Element(name = 'CLK3_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 3 Invert.'),
                                          Element(name = 'CLK3_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 3 Input Source.'),
                                          Element(name = 'CLK3_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK3 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK4_Control', address = 20, description = 'CLK4_Control',
                              elements = [Element(name = 'CLK4_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 4 Power Down.'),
                                          Element(name = 'MS4_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 4 Integer Mode.'),
                                          Element(name = 'MS4_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK4.'),
                                          Element(name = 'CLK4_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 4 Invert.'),
                                          Element(name = 'CLK4_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 4 Input Source.'),
                                          Element(name = 'CLK4_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK4 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK5_Control', address = 21, description = 'CLK5_Control',
                              elements = [Element(name = 'CLK5_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 5 Power Down.'),
                                          Element(name = 'MS5_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'MultiSynth 5 Integer Mode.'),
                                          Element(name = 'MS5_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK5.'),
                                          Element(name = 'CLK5_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 5 Invert.'),
                                          Element(name = 'CLK5_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 5 Input Source.'),
                                          Element(name = 'CLK5_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK5 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK6_Control', address = 22, description = 'CLK6_Control',
                              elements = [Element(name = 'CLK6_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 7 Power Down.'),
                                          Element(name = 'FBA_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'FBA MultiSynth Integer Mode.'),
                                          Element(name = 'MS6_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK6.'),
                                          Element(name = 'CLK6_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 6 Invert.'),
                                          Element(name = 'CLK6_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 6 Input Source.'),
                                          Element(name = 'CLK6_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK6 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK7_Control', address = 23, description = 'CLK7_Control',
                              elements = [Element(name = 'CLK7_PDN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Clock 7 Power Down.'),
                                          Element(name = 'FBB_INT', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'FBB MultiSynth Integer Mode.'),
                                          Element(name = 'MS7_SRC', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'MultiSynth Source Select for CLK7.'),
                                          Element(name = 'CLK7_INV', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Output Clock 7 Invert.'),
                                          Element(name = 'CLK7_SRC', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Output Clock 7 Input Source.'),
                                          Element(name = 'CLK7_IDRV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'CLK7 Output Rise and Fall time / Drive Strength Control.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK3_0_Disable_State', address = 24, description = 'CLK3_0_Disable_State',
                              elements = [Element(name = 'CLK3_DIS_STATE', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'Clock 3 Disable State.'),
                                          Element(name = 'CLK2_DIS_STATE', idx_lowest_bit = 4, n_bits = 2, value = 0,
                                                  description = 'Clock 2 Disable State.'),
                                          Element(name = 'CLK1_DIS_STATE', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Clock 1 Disable State.'),
                                          Element(name = 'CLK0_DIS_STATE', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Clock 0 Disable State.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'CLK7_4_Disable_State', address = 25, description = 'CLK7_4_Disable_State',
                              elements = [Element(name = 'CLK7_DIS_STATE', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'Clock 7 Disable State.'),
                                          Element(name = 'CLK6_DIS_STATE', idx_lowest_bit = 4, n_bits = 2, value = 0,
                                                  description = 'Clock 6 Disable State.'),
                                          Element(name = 'CLK5_DIS_STATE', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  description = 'Clock 5 Disable State.'),
                                          Element(name = 'CLK4_DIS_STATE', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Clock 4 Disable State.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 26, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 27, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 28, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'Unused', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Unused.'),
                                          Element(name = 'Reserved_2', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                                  read_only = True, description = 'Reserved.'),
                                          Element(name = 'MSNA_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                                  description = 'Multisynth NA Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 29, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 30, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 31, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          Element(name = 'MSNA_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth NA Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 32, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NA_Parameters', address = 33, description = 'Multisynth_NA_Parameters',
                              elements = [Element(name = 'MSNA_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 34, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NA Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 35, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 36, description = 'Multisynth_NB_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 4, n_bits = 4, value = 0, description = ''),
                                  Element(name = 'Reserved_2', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          read_only = True, description = 'Reserved.'),
                                  Element(name = 'MSNB_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth NB Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 37, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 38, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 39, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth NB Parameter 3.'),
                                          Element(name = 'MSNB_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth NB Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 40, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth_NB_Parameters', address = 41, description = 'Multisynth_NB_Parameters',
                              elements = [Element(name = 'MSNB_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth NB Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 42, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 43, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 44, description = 'Multisynth0_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R0_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R0 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS0_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS0 Divide by 4 Enable.'),
                                  Element(name = 'MS0_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth0 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 45, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 46, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 47, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth0 Parameter 3.'),
                                          Element(name = 'MS0_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth0 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 48, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth0_Parameters', address = 49, description = 'Multisynth0_Parameters',
                              elements = [Element(name = 'MS0_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth0 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 50, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 51, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 52, description = 'Multisynth1_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R1_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R1 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS1_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS1 Divide by 4 Enable.'),
                                  Element(name = 'MS1_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth1 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 53, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 54, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 55, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth1 Parameter 3.'),
                                          Element(name = 'MS1_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth1 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 56, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth1_Parameters', address = 57, description = 'Multisynth1_Parameters',
                              elements = [Element(name = 'MS1_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth1 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 58, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 59, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 60, description = 'Multisynth2_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R2_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R2 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS2_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS2 Divide by 4 Enable.'),
                                  Element(name = 'MS2_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth2 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 61, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 62, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 63, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth2 Parameter 3.'),
                                          Element(name = 'MS2_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth2 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 64, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth2_Parameters', address = 65, description = 'Multisynth2_Parameters',
                              elements = [Element(name = 'MS2_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth2 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 66, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 67, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 68, description = 'Multisynth3_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R3_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R3 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS3_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS3 Divide by 4 Enable.'),
                                  Element(name = 'MS3_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth3 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 69, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 70, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 71, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth3 Parameter 3.'),
                                          Element(name = 'MS3_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth3 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 72, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth3_Parameters', address = 73, description = 'Multisynth3_Parameters',
                              elements = [Element(name = 'MS3_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth3 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 74, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 75, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 76, description = 'Multisynth4_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R4_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R4 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS4_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS4 Divide by 4 Enable.'),
                                  Element(name = 'MS4_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth4 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 77, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 78, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 79, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth4 Parameter 3.'),
                                          Element(name = 'MS4_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth4 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 80, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth4_Parameters', address = 81, description = 'Multisynth4_Parameters',
                              elements = [Element(name = 'MS4_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth4 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 82, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P3_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 83, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 3.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 84, description = 'Multisynth5_Parameters',
                              elements = [
                                  Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = ''),
                                  Element(name = 'R5_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                          description = 'R5 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                                  Element(name = 'MS5_DIVBY4', idx_lowest_bit = 2, n_bits = 2, value = 0,
                                          description = 'MS5 Divide by 4 Enable.'),
                                  Element(name = 'MS5_P1_17_16', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                          description = 'Multisynth5 Parameter 1.'),
                                  ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 85, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P1_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 86, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 87, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P3_19_16', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                                  description = 'Multisynth5 Parameter 3.'),
                                          Element(name = 'MS5_P2_19_16', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                                  description = 'Multisynth5 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 88, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P2_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth5_Parameters', address = 89, description = 'Multisynth5_Parameters',
                              elements = [Element(name = 'MS5_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth5 Parameter 2.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth6_Parameters', address = 90, description = 'Multisynth6_Parameters',
                              elements = [Element(name = 'MS6_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth6 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Multisynth7_Parameters', address = 91, description = 'Multisynth7_Parameters',
                              elements = [Element(name = 'MS7_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'Multisynth7 Parameter 1.'),
                                          ], default_value = 0))

    registers.append(
        Register(name = 'Clock_6_and_7_Output_Divider', address = 92, description = 'Clock_6_and_7_Output_Divider',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Leave as default.'),
                             Element(name = 'R7_DIV', idx_lowest_bit = 4, n_bits = 3, value = 0,
                                     description = 'R7 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                             Element(name = 'Reserved_3', idx_lowest_bit = 3, n_bits = 1, value = 0, read_only = True,
                                     description = 'Leave as default.'),
                             Element(name = 'R6_DIV', idx_lowest_bit = 0, n_bits = 2, value = 0,
                                     description = 'R6 Output Divider. 000b: Divide by 1 001b: Divide by 2'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 149, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSC_EN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                     description = 'Spread Spectrum Enable'),
                             Element(name = 'SSDN_P2_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 2.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 150, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSDN_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 2.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 151, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSC_MODE', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                     description = 'Spread Spectrum Mode.'),
                             Element(name = 'SSDN_P3_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 3.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 152, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSDN_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 3.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 153, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSDN_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 1.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 154, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUDP_11_8', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                     description = 'PLL A Spread Spectrum Up/Down Parameter.'),
                             Element(name = 'SSDN_P1_11_8', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                     description = 'PLL A Spread Spectrum Down Parameter 1.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 155, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUDP_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up/Down Parameter.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 156, description = 'Spread_Spectrum_Parameters',
                 elements = [
                     Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = 'Unused.'),
                     Element(name = 'SSUP_P2_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                             description = 'PLL A Spread Spectrum Up Parameter 2.'),
                     ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 157, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUP_P2_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 2.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 158, description = 'Spread_Spectrum_Parameters',
                 elements = [
                     Element(name = 'Unused', idx_lowest_bit = 7, n_bits = 1, value = 0, description = 'Unused.'),
                     Element(name = 'SSUP_P3_14_8', idx_lowest_bit = 0, n_bits = 7, value = 0,
                             description = 'PLL A Spread Spectrum Up Parameter 3.'),
                     ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 159, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUP_P3_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 3.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 160, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SSUP_P1_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 1.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'Spread_Spectrum_Parameters', address = 161, description = 'Spread_Spectrum_Parameters',
                 elements = [Element(name = 'SS_NCLK', idx_lowest_bit = 4, n_bits = 4, value = 0,
                                     description = 'Must write 0000b to these bits.'),
                             Element(name = 'SSUP_P1_11_8', idx_lowest_bit = 0, n_bits = 4, value = 0,
                                     description = 'PLL A Spread Spectrum Up Parameter 1.'),
                             ], default_value = 0))

    registers.append(Register(name = 'VCXO_Parameter', address = 162, description = 'VCXO_Parameter',
                              elements = [Element(name = 'VCXO_Param_7_0', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'VCXO Parameter.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'VCXO_Parameter', address = 163, description = 'VCXO_Parameter',
                              elements = [Element(name = 'VCXO_Param_15_8', idx_lowest_bit = 0, n_bits = 8, value = 0,
                                                  description = 'VCXO Parameter.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'VCXO_Parameter', address = 164, description = 'VCXO_Parameter',
                              elements = [Element(name = 'Reserved_6', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  read_only = True,
                                                  description = 'Reserved. Only write 00b to these bits.'),
                                          Element(name = 'VCXO_Param_21_16', idx_lowest_bit = 0, n_bits = 6, value = 0,
                                                  description = 'VCXO Parameter.'),
                                          ], default_value = 0))

    registers.append(
        Register(name = 'CLK0_Initial_Phase_Offset', address = 165, description = 'CLK0_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK0_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 0 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK1_Initial_Phase_Offset', address = 166, description = 'CLK1_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK1_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 1 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK2_Initial_Phase_Offset', address = 167, description = 'CLK2_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK2_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 2 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK3_Initial_Phase_Offset', address = 168, description = 'CLK3_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK3_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 3 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK4_Initial_Phase_Offset', address = 169, description = 'CLK4_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK4_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 4 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(
        Register(name = 'CLK5_Initial_Phase_Offset', address = 170, description = 'CLK5_Initial_Phase_Offset',
                 elements = [Element(name = 'Reserved_7', idx_lowest_bit = 7, n_bits = 1, value = 0, read_only = True,
                                     description = 'Only write 0 to this bit.'),
                             Element(name = 'CLK5_PHOFF', idx_lowest_bit = 0, n_bits = 7, value = 0,
                                     description = 'Clock 5 Initial Phase Offset.'),
                             ], default_value = 0))

    registers.append(Register(name = 'PLL_Reset', address = 177, description = 'PLL_Reset',
                              elements = [Element(name = 'PLLB_RST', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'PLLB_Reset.'),
                                          Element(name = 'Reserved_6', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          Element(name = 'PLLA_RST', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  description = 'PLLA_Reset.'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 5, value = 0,
                                                  read_only = True, description = 'Leave as default.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Crystal_Internal_Load_Capacitance', address = 183,
                              description = 'Crystal_Internal_Load_Capacitance',
                              elements = [Element(name = 'XTAL_CL', idx_lowest_bit = 6, n_bits = 2, value = 0,
                                                  description = 'Crystal Load Capacitance Selection.'),
                                          Element(name = 'Reserved_0', idx_lowest_bit = 0, n_bits = 6, value = 0,
                                                  read_only = True,
                                                  description = 'Bits 5:0 should be written to 010010b.'),
                                          ], default_value = 0))

    registers.append(Register(name = 'Fanout_Enable', address = 187, description = 'Fanout_Enable',
                              elements = [Element(name = 'CLKIN_FANOUT_EN', idx_lowest_bit = 7, n_bits = 1, value = 0,
                                                  description = 'Enable fanout of CLKIN to clock output multiplexers. Set this bit to 1b.'),
                                          Element(name = 'XO_FANOUT_EN', idx_lowest_bit = 6, n_bits = 1, value = 0,
                                                  description = 'Enable fanout of XO to clock output multiplexers. Set this bit to 1b.'),
                                          Element(name = 'Reserved_5', idx_lowest_bit = 5, n_bits = 1, value = 0,
                                                  read_only = True, description = 'Reserved.'),
                                          Element(name = 'MS_FANOUT_EN', idx_lowest_bit = 4, n_bits = 1, value = 0,
                                                  description = 'Enable fanout of Multisynth0 and Multisynth4 to all output multiplexers. Set this bit to 1b.'),
                                          ], default_value = 0))

    return registers



def _get_registers_map():
    raw_registers = _get_all_raw_registers()

    names = [reg.name for reg in raw_registers]
    duplicated_names = list((n for n in set(names) if names.count(n) > 1))

    for reg in raw_registers:
        if reg.name in duplicated_names:
            reg.name = '{}_{}'.format(reg.name, reg.address)

    regs_map = RegistersMap(name = 'Si5351', description = 'Si5351 registers.', registers = raw_registers)

    reg = regs_map.registers['Crystal_Internal_Load_Capacitance']
    reg.default_value = 0xC0
    reg.reset()

    element = regs_map.elements['SS_NCLK']['element']
    element.value = 0
    element.read_only = True

    return regs_map



class Si535x(Device):
    N_OUTPUT_CLOCKS = 8
    PLLs = ('A', 'B')
    N_PLLS = len(PLLs)
    CLKIN_DIVIDERS = {1: 0x00, 2: 0x01, 4: 0x20, 8: 0x03}
    FREQ_MCLK = int(25e6)
    I2C_ADDRESS = 0x60
    DENOMINATOR_BITS = 20

    READ_ONLY_REGISTERS = (0,)
    CLOCK_SOURCEs = {'XTAL': 0x00, 'CLKIN': 0x01, 'MultiSynth': 0x3}
    OUTPUT_STRENGTHs = {2: 0x00, 4: 0x01, 6: 0x02, 8: 0x03}
    CRYSTAL_INTERNAL_LOAD_CAPACITANCEs = {6: 0x01, 8: 0x02, 10: 0x03}
    DISABLE_STATEs = {'LOW': 0x00, 'HIGH': 0x01, 'HIGH_IMPEDANCE': 0x02, 'NEVER_DISABLED': 0x03}
    R_DIVIDERs = {1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6, 128: 7}

    # ['0', '1', '2', '3', '4', '5', '6', '7', 'NA', 'NB']
    MULTISYNTH_NAMEs = list((str(i) for i in range(N_OUTPUT_CLOCKS))) + list(('N' + e for e in PLLs))


    class _Interrupts:

        def __init__(self, si):
            self._si = si


        def set_interrupts_mask(self, mask = 0):
            self._si._write_register_by_name('Interrupt_Status_Mask', mask)


        def set_interrupt_mask(self, interrupt_name, value = True):
            self._si._write_element_by_name('{}_MASK'.format(interrupt_name.upper()), 1 if value else 0)


        def read_interrupt_stickys(self):
            return self._si._read_register_by_name('Interrupt_Status_Sticky')


        def clear_interrupt_stickys(self):
            self._si._write_register_by_name('Interrupt_Status_Sticky', 0)


        def clear_interrupt_sticky(self, interrupt_name):
            self._si._write_element_by_name('{}_STKY'.format(interrupt_name.upper()), 0)


    class _Crystal:

        def __init__(self, si):
            self._si = si


        # crystal capacitance
        def set_crystal_internal_load_capacitance(self, pF = 10):
            """
            If the source for the PLL is a crystal, PLLx_SRC must be set to 0 in register 15. XTAL_CL[1:0] must also be set to
            match the crystal load capacitance (see register 183).
            """
            self._si._write_element_by_name('XTAL_CL', self._si.CRYSTAL_INTERNAL_LOAD_CAPACITANCEs[pF])


        def get_freq_vco_xtal(self, freq_xtal, a, b, c):
            return freq_xtal * (a + b / c)


        def get_freq_vco_clkin(self, freq_clkin, clkin_div, a, b, c):
            return freq_clkin / clkin_div * (a + b / c)


        def set_vcxo_paramenters(self, a, b, apr = 30):
            """
            The Si5351B combines free-running clock generation and a VCXO in a single package. The VCXO architecture of
            the Si5350B eliminates the need for an external pullable crystal. The “pulling” is done at PLLB. Only a standard,
            low cost, fixed-frequency (25 or 27 MHz) AT-cut crystal is required and is used as the reference source for both
            PLLA and PLLB.
            PLLB must be used as the source for any VCXO output clock. Feedback B Multisynth divider ratio must be set
            such that the denominator, c, in the fractional divider a + b/c is fixed to 106. Set VCXO_Param register value
            according to the equation below. Note that 1.03 is a margining factor to ensure the full desired pull range is
            achieved. For a desired pull-range of +/– 30 ppm, the value APR in the equation below is 30, for +/– 60 ppm APR
            is 60, and so on.

            VCXO_Param[21:0] =  1.03 * (128a +  b/10**6) * APR
            """

            vcxo_p = 1.03 * (128 * a + b / 10 ** 6) * apr

            bits_ranges = ((21, 16), (15, 8), (7, 0))

            for bits_range in bits_ranges:
                element_name = 'VCXO_Param_{}_{}'.format(bits_range[0], bits_range[1])
                mask = (2 ** (bits_range[0] - bits_range[1] + 1) - 1) << bits_range[1]
                value = (vcxo_p & mask) >> bits_range[1]
                self._si._write_element_by_name(element_name, value)


        def enable_xo_fanout(self, value = True):
            self._si._write_element_by_name('XO_FANOUT_EN', 1 if value else 0)


    class _PLLs:

        def __init__(self, si):
            self._si = si
            self._pll_clkin_freq = self._si.freq_mclk


        def reset_plls(self):
            self._si._write_register_by_name('PLL_Reset', 0xA0)
            self._si._read_register_by_name('PLL_Reset')  # Synch. These are self clearing bits.


        def reset_pll(self, idx):
            element_name = 'PLL{}_RST'.format(self._si.PLLs[idx])
            self._si._write_element_by_name(element_name, 1)
            self._si._read_element_by_name(element_name)  # Synch. This is a self clearing bit.


        def set_pll_input_source(self, idx, xtal_as_source = True):
            """
            If a PLL needs to be synchronized to a CMOS clock, PLLx_SRC must be 1.
            The input frequency range of the PLL is 10 to 40 MHz. If CLKIN is > 40 MHz,
            the CLKIN input divider must be used to bring the PLL input within the 10–40 MHz range.
            See CLKIN_DIV[1:0], register 15, bits [7:6].
            """
            element_name = 'PLL{}_SRC'.format(self._si.PLLs[idx])
            self._si._write_element_by_name(element_name, 0 if xtal_as_source else 1)
            self.set_pll_clkin_divider()


        @property
        def pll_clkin_freq(self):
            return self._pll_clkin_freq


        def set_pll_clkin_divider(self):
            for d in sorted(self._si.CLKIN_DIVIDERS.keys()):
                if self._si.freq_mclk / d <= 40e6:
                    break
            assert self._si.freq_mclk / d <= 40e6, 'The input frequency range of the PLLis 10 to 40 MHz'
            self._pll_clkin_freq = int(self._si.freq_mclk / d)
            self._si._write_element_by_name('CLKIN_DIV', self._si.CLKIN_DIVIDERS[d])


    class _Multisynthes:

        def __init__(self, si):
            self._si = si


        def get_pll_multisynth_divider(self, a, b, c):
            assert 15 + 1 / ((2 ** self._si.DENOMINATOR_BITS) - 1) <= a <= 90, \
                'Must 15 + 1 / ((2 ** {}) - 1) <= a <= 90'.format(self._si.DENOMINATOR_BITS)

            p1 = 128 * a + math.floor(128 * b / c) - 512
            p2 = 128 * b - c * math.floor(128 * b / c)
            p3 = c
            return p1, p2, p3


        def get_output_multisynth_divider(self, a, b, c):
            """
             MS6 and MS7 are integer-only dividers. The valid range
            of values for these dividers is all even integers between 6 and 254 inclusive. For MS6 and MS7, set MSx_P1
            directly (e.g., MSx_P1=divide value).
            """
            assert 15 + 1 / ((2 ** self._si.DENOMINATOR_BITS) - 1) <= a <= 90, \
                'Must 15 + 1 / ((2 ** {}) - 1) <= a <= 90'.format(self._si.DENOMINATOR_BITS)

            p1 = 128 * a + math.floor(128 * b / c) - 512
            p2 = 128 * b - c * math.floor(128 * b / c)
            p3 = c
            return p1, p2, p3


        def set_multisynth_integer_mode(self, idx, value = True):
            assert idx in range(6)
            self._si._write_element_by_name('MS{}_INT'.format(idx), 1 if value else 0)


        def force_pll_feedback_multisynth_integer_mode(self, idx, value = True):
            """
            If a + b/c is an even integer, integer mode may be enabled for PLLA or PLLB by setting parameter FBA_INT or
            FBB_INT respectively. In most cases setting this bit will improve jitter when using even integer divide values.
            Whenever spread spectrum is enabled, FBA_INT must be set to 0.
            """
            assert idx in (6, 7)
            self._si._write_element_by_name('FB{}_INT'.format(self._si.PLLs[idx - 6]), 1 if value else 0)


        def set_multisynth_source(self, idx, pll_idx = 0):
            """
            Each of these dividers can be set to use PLLA or PLLB as its reference by setting MSx_SRC to 0 or 1 respectively.
            See bit 5 description of registers 16-23.
            """
            self._si._write_element_by_name('MS{}_SRC'.format(idx), pll_idx)


        def set_multisynth_divided_by_4(self, idx, value = True):
            """
            Output frequencies greater than 150 MHz are available on Multisynths 0-5. For this frequency range a divide value
            of 4 must be used by setting
            MSx_P1=0,
            MSx_P2=0,
            MSx_P3=1,
            MSx_INT=1, and
            MSx_DIVBY4[1:0]=11b.
            Set the appropriate feedback Multisynth to generate fVCO=Fout*4.
            """
            self._si._write_element_by_name('MS{}_DIVBY4'.format(idx), 0x03 if value else 0x00)


        def set_multisynth_parameters(self, multisynth_name, p1, p2 = None, p3 = None):
            params = (p1, p2, p3)

            bits_8 = ((7, 0))
            bits_18 = ((17, 16), (15, 8), (7, 0))
            bits_20 = ((19, 16), (15, 8), (7, 0))

            bits_ranges = {1: bits_8, 2: [], 3: []} if multisynth_name in ['6', '7'] else \
                {1: bits_18, 2: bits_20, 3: bits_20}

            for i in range(len(params)):
                param_idx = i + 1
                for bits_range in bits_ranges[param_idx]:
                    element_name = 'MS{}_P{}_{}_{}'.format(multisynth_name, param_idx, bits_range[0], bits_range[1])
                    mask = (2 ** (bits_range[0] - bits_range[1] + 1) - 1) << bits_range[1]
                    value = (params[i] & mask) >> bits_range[1]
                    self._si._write_element_by_name(element_name, value)


        def enable_multisynth_fanout(self, value = True):
            self._si._write_element_by_name('MS_FANOUT_EN', 1 if value else 0)


        def is_even_integer(self, v):
            return abs(v - int(v)) < 10 ** (-self._si.DENOMINATOR_BITS) and int(v) % 2 == 0


        def is_abc_even_integer(self, a, b, c):
            return self.is_even_integer(a + b / c)


    class _Clocks:

        def __init__(self, si):
            self._si = si


        def set_clock_source(self, idx, source = 'MultiSynth'):
            """
            Generally, Multisynth x should be output on CLKx, however XO, CLKIN, or a divided version of either (see section
            4.2.2 on R dividers) may also be output on each of the CLKx pins. Additionally, MS0 (or a divided version of MS0)
            may be output on CLK0-CLK3, and MS4 (or a divided version of MS4) may be output on CLK4-CLK7. See
            CLKx_SRC description for details.
            """
            self._si._write_element_by_name('CLK{}_SRC'.format(idx), self._si.CLOCK_SOURCEs[source])


        def set_clock_strength(self, idx, strength = 8):
            self._si._write_element_by_name('CLK{}_IDRV'.format(idx), self._si.OUTPUT_STRENGTHs[strength])


        def set_clock_invert(self, idx, value = True):
            self._si._write_element_by_name('CLK{}_INV'.format(idx), 1 if value else 0)


        def enable_all_outputs(self, value = True):
            self._si._action = 'enable_all_outputs: {}'.format(value)
            self._si._write_register_by_name('Output_Enable_Control', 0x00 if value else 0xFF)


        def enable_output_clock(self, idx, value = True):
            self._si._action = 'enable_output_clock: {} {}'.format(idx, value)
            self._si._write_element_by_name('CLK{}_OEB'.format(idx), 0 if value else 1)


        def mask_output_clock_oeb(self, idx, value = True):
            self._si._action = 'enable_output_clock_oeb_mask: {} {}'.format(idx, value)
            self._si._write_element_by_name('OEB_MASK{}'.format(idx), 1 if value else 0)


        def set_clock_disable_state(self, idx, state = 'LOW'):
            self._si._write_element_by_name('CLK{}_DIS_STATE'.format(idx), self._si.DISABLE_STATEs[state])


        def power_down_all_outputs(self, value = True):
            for i in range(self._si.N_OUTPUT_CLOCKS):
                self.power_down_output_clock(idx = i, value = value)


        def power_down_output_clock(self, idx, value = True):
            self._si._write_element_by_name('CLK{}_PDN'.format(idx), 1 if value else 0)


        def set_r_divider(self, idx, divider = 1):
            """
            The R dividers can be used to generate frequencies below about 500 kHz. Each individual output R divider can be
            set to 1, 2, 4, 8,....128 by writing the proper setting for Rx_DIV. Set this parameter to generate frequencies down to
            8kHz
            """
            assert divider in self._si.R_DIVIDERs.keys()
            self._si._write_element_by_name('R{}_DIV'.format(idx), self._si.R_DIVIDERs[divider])


        def enable_phase_offset(self, offset_seconds, freq_vco):
            """
            However, it's important to note that Multisynth integer mode cannot be used when adding phase offsets in NVM. In
            other words, MSx_INT needs to be set to 0 if phase offsets need to be enabled.

              Outputs 0-5 of the Si5351 can be programmed with an independent initial phase offset. The phase offset only
            works when MS0-5 are set as fractional dividers (divider values greater than 8). The phase offset parameter is an
            unsigned integer where each LSB represents a phase difference of a quarter of the VCO period, TVCO/4. Use the
            equation below to determine the register value. Also, remember that any divider using the phase offset feature
            needs the MSx_INT bit set to 0.

            CLKx_PHOFF[4:0] = Round(DesiredOffset_sec * 4 * FVCO)
            """

            offset = round(offset_seconds * 4 * freq_vco)


        def set_clock_initial_phase_offset(self, idx, value = 0):
            """
            CLKx_PHOFF[6:0] is an unsigned integer with one LSB equivalent to a time delay of
            Tvco/4, where Tvco is the period of the VCO/PLL associated with this output.
            """
            assert idx in range(6)
            self._si._write_element_by_name('CLK{}_PHOFF'.format(idx), value & 0x3F)


        def enable_clkin_fanout(self, value = True):
            self._si._write_element_by_name('CLKIN_FANOUT_EN', 1 if value else 0)


    class _SpreadSpectrum:

        def __init__(self, si):
            self._si = si


        def enable_spread_spectrum(self, value = True):
            """
            spread spectrum is only supported by PLLA, and the VCXO functionality is only
            supported by PLLB. When using the VCXO function, set the MSNB divide ratio a + b/c such that c = 10**6. This must
            be taken into consideration when configuring a frequency plan.
              Whenever spread spectrum is enabled, FBA_INT must be set to 0.

              The Spread Spectrum Enable control pin is available on the Si5351A and B devices. Spread spectrum enable
            functionality is a logical OR of the SSEN pin and SSC_EN register bit, so for the SSEN pin to work properly, the
            SSC_EN register bit must be set to 0.
            """

            self._si._write_element_by_name('SSC_EN', 1 if value else 0)


        def set_down_spread_spectrum(self, freq_pfd, ssc_amp, a, b, c):
            """
            For down spread, four spread spectrum parameters need to be written: SSUDP[11:0], SSDN_P1[11:0],
            SSDN_P2[14:0], and SSDN_P3[14:0].
            """
            ssudp = math.floor(freq_pfd / (4 * 31500))

            ssdn = 64 * (a + b / c) * ssc_amp / ((1 + ssc_amp) * ssudp)
            ssdn_p1 = math.floor(ssdn)
            ssdn_p2 = 32767 * (ssdn - ssdn_p1)
            ssdn_p3 = 32767

            ssup_p1 = 0,
            ssup_p2 = 0
            ssup_p3 = 1

            self.set_spread_spectrum_parameters('UDP', ssudp)
            self.set_spread_spectrum_parameters('UP', ssup_p1, ssup_p2, ssup_p3)
            self.set_spread_spectrum_parameters('DN', ssdn_p1, ssdn_p2, ssdn_p3)

            return ssudp, (ssup_p1, ssup_p2, ssup_p3), (ssdn_p1, ssdn_p2, ssdn_p3)


        def set_center_spread_spectrum(self, freq_pfd, ssc_amp, a, b, c):
            """
            For center spread, seven spread spectrum parameters need to be written: SSUDP[11:0], SSDN_P1[11:0],
            SSDN_P2[14:0], SSDN_P3[14:0], SSUP_P1[11:0], SSUP_P2[14:0], and SSUP_P3[14:0].
            """

            ssudp = math.floor(freq_pfd / (4 * 31500))

            ssup = 128 * (a + b / c) * ssc_amp / ((1 - ssc_amp) * ssudp)
            ssup_p1 = math.floor(ssup)
            ssup_p2 = 32767 * (ssup - ssup_p1)
            ssup_p3 = 32767

            ssdn = 128 * (a + b / c) * ssc_amp / ((1 + ssc_amp) * ssudp)
            ssdn_p1 = math.floor(ssdn)
            ssdn_p2 = 32767 * (ssdn - ssdn_p1)
            ssdn_p3 = 32767

            self.set_spread_spectrum_parameters('UDP', ssudp)
            self.set_spread_spectrum_parameters('UP', ssup_p1, ssup_p2, ssup_p3)
            self.set_spread_spectrum_parameters('DN', ssdn_p1, ssdn_p2, ssdn_p3)

            return ssudp, (ssup_p1, ssup_p2, ssup_p3), (ssdn_p1, ssdn_p2, ssdn_p3)


        def set_spread_spectrum_parameters(self, name, p1, p2 = None, p3 = None):
            """
            Spread spectrum can be enabled on any Multisynth output that uses PLLA as its reference. Valid ranges for spread
            spectrum include –0.1% to –2.5% down spread and up to ± 1.5% center spread. This spread modulation rate is
            fixed at approximately 31.5 kHz.
            The following parameters must be known to properly set up spread spectrum:
            fPFD(A) input frequency to PLLA in Hz (determined in Sec 2 above and referred to in “3.1.2. CMOS Clock
            Source”). This is also listed in the ClockBuilder Pro generated register map file as “#PFD(MHz)=...”
            a + b/c PLLA Multisynth ratio (determined in Sec 2 above).
            sscAMPSpread amplitude (e.g., for down or center spread amplitude of 1%, sscAmp = 0.01).
            Use the equations below to set up the desired spread spectrum profile.
            Note: Make sure MSNA is set up in fractional mode when using the spread spectrum feature. See parameter FBA_INT in register 22.
            """
            assert name in ('UP', 'DN', 'UDP')
            params = (p1, p2, p3)
            bits_12 = ((11, 8), (7, 0))
            bits_15 = ((14, 8), (7, 0))
            bits_ranges = {1: bits_12, 2: [], 3: []} if name == 'UDP' else {1: bits_12, 2: bits_15, 3: bits_15}

            for i in range(len(params)):
                param_idx = i + 1
                element_name = 'SSUDP' if name == 'UDP' else 'SS{}_P{}'.format(name, param_idx)
                for bits_range in bits_ranges[param_idx]:
                    element_name = '{}_{}_{}'.format(element_name, bits_range[0], bits_range[1])
                    mask = (2 ** (bits_range[0] - bits_range[1] + 1) - 1) << bits_range[1]
                    value = (params[i] & mask) >> bits_range[1]
                    self._si._write_element_by_name(element_name, value)


    def __init__(self, i2c, i2c_address = I2C_ADDRESS, pin_oeb = None, pin_ssen = None,
                 registers_map = None, registers_values = None,
                 n_channels = N_OUTPUT_CLOCKS, freq_mclk = FREQ_MCLK,
                 commands = None):

        registers_map = _get_registers_map() if registers_map is None else registers_map

        super().__init__(n_channels = n_channels, freq_mclk = freq_mclk,
                         registers_map = registers_map, registers_values = registers_values,
                         commands = commands)

        self._i2c = I2C(i2c, i2c_address)
        self._i2c_address = i2c_address
        self._pin_oeb = pin_oeb
        self._pin_ssen = pin_ssen

        self.interrupts = self._Interrupts(self)
        self.crystal = self._Crystal(self)
        self.plls = self._PLLs(self)
        self.multisynthes = self._Multisynthes(self)
        self.clocks = self._Clocks(self)
        self.spread_spectrum = self._SpreadSpectrum(self)

        self.init()


    def init(self):

        # step 4: define inputs and features
        #     input mode
        #         mode enable/disable
        #         frequency 25/27 MHz
        #         internal load 0/6/8/10 pF
        #     Feature
        #         Spread Spectrum Clock Config
        #             enable True/False
        #             direction down/center
        #             amplitude 0.1%
        # step 5: define output frequencies
        #     Out0
        #         mode enabled/disabled/unused
        #         frequency ??? Hz (ex. 19.2MHz, 2*IN0, OUT5, OUT5 + 5ppb)
        #         feature SSC
        #     Out1
        #     ...
        # step 6: define output skews
        #     Out0
        #         desired skew 6ns  ==> Actual_Skew = 6.127ns,  CLK0_PHOFF = 0x16
        #     Out1
        #     ...
        # step 7: define output driver configuration
        #     Out1
        #         format driver_strength 2/4/6/8mA
        #         disable state stop_low/stop_high/HiZ

        self._action = 'init'
        self.enable_output(False)
        self.start()


    def enable_output(self, value = True):
        self._action = 'enable_output: {}'.format(value)
        self.clocks.enable_all_outputs(value)


    def enable(self, value):
        self._action = 'enable {}'.format(value)
        self.clocks.power_down_all_outputs(not value)
        self.enable_output(value)


    @property
    def status(self):
        return self._read_register_by_name('Device_Status')


    # =================================================================

    def _write_register(self, register, reset = False):
        if register.address not in self.READ_ONLY_REGISTERS:
            super()._write_register(register, reset = reset)
            return self._i2c.write_byte(register.address, register.value)


    def _read_register(self, register):
        value = self._i2c.read_byte(register.address)
        self._show_bus_data(bytes([value]), address = register.address, reading = True)
        self._print_register(register)
        return value
