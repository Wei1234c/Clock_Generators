# https://www.silabs.com/documents/public/data-sheets/Si5351-B.pdf
# https://www.silabs.com/documents/public/application-notes/AN619.pdf
# https://groups.io/g/BITX20/topic/si5351a_facts_and_myths/5430607
# https://www.silabs.com/content/usergenerated/asi/cloud/attachments/siliconlabs/en/community/groups/timing/knowledge-base/jcr:content/content/primary/blog/modifying_the_feedba-K8Pv/311668.pdf


try:
    from collections import OrderedDict
    from ..interfaces import *
    from utilities.adapters.peripherals import I2C
    from .reg_map.map_manager import _get_registers_map
except:
    from collections import OrderedDict
    from interfaces import *
    from peripherals import I2C
    from map_manager import _get_registers_map



def _section_value(value, idx_msb, idx_lsb):
    mask = (2 ** (idx_msb - idx_lsb + 1) - 1) << idx_lsb
    return (value & mask) >> idx_lsb



def _value_key(dictionary):
    return {v: k for k, v in dictionary.items()}



class Si5351A_B_GT(Device):
    I2C_ADDRESS = 0x60
    READ_ONLY_REGISTERS = (0,)

    FREQ_REF = int(25e6)

    N_OUTPUT_CLOCKS = 3
    OUTPUT_CLOCKS_IN_USE = (0, 1, 2)

    HAS_VCXO = False


    class _Interrupts:

        def __init__(self, si, masks = 0x00):
            self._si = si
            self.set_masks(masks)
            self.clear_stickys()


        @property
        def masks(self):
            return self._si._read_register_by_name('Interrupt_Status_Mask')


        def set_masks(self, masks = 0x00):
            self._si._action = 'set_masks {}'.format(masks)
            self._si._write_register_by_name('Interrupt_Status_Mask', masks)


        def set_mask(self, interrupt_name, value = True):
            self._si._action = 'set_mask {} {}'.format(interrupt_name, value)

            valids = self._si.map.registers['Interrupt_Status_Mask'].elements.keys()
            assert interrupt_name in valids, 'valid names: {}'.format(valids)

            self._si._write_element_by_name('{}_MASK'.format(interrupt_name.upper()), 1 if value else 0)


        @property
        def stickys(self):
            return self._si._read_register_by_name('Interrupt_Status_Sticky')


        def clear_stickys(self):
            self._si._action = 'clear_stickys'
            self._si._write_register_by_name('Interrupt_Status_Sticky', 0x00)


        def clear_sticky(self, interrupt_name):
            self._si._action = 'clear_sticky {}'.format(interrupt_name)

            valids = self._si.map.registers['Interrupt_Status_Sticky'].elements.keys()
            assert interrupt_name in valids, 'valid names: {}'.format(valids)

            self._si._write_element_by_name('{}_STKY'.format(interrupt_name.upper()), 0)


    class _MultisynthBase:
        DIVIDER_MIN = None
        DIVIDER_MAX = None
        DIVIDER_DEFAULT = None

        DENOMINATOR_BITS = 20
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1

        N_HIGH_FREQUENCY_MULTISYNTHS = 6
        N_MULTISYNTHS_WITH_OUTPUT_SKEW = 6
        INTEGER_ONLY_MULTISYNTHS = (6, 7)


        def __init__(self, si, idx, denominator_max = DENOMINATOR_MAX):
            self._si = si
            self._idx = idx

            self.denominator_max = denominator_max
            self._source = None
            self._set_divider(self.DIVIDER_DEFAULT)
            # self.set_input_source()  # need implement


        @property
        def name(self):
            return str(self._idx)


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'idx'        : self._idx,
                                'source_type': self.source.__class__.__name__,
                                'source_idx' : self.source._idx,
                                'source_freq': self.source.freq,
                                'my_freq'    : self.freq,
                                'my_divider' : self.divider})


        @property
        def source(self):
            return self._source


        def set_input_source(self, source):
            self._si._action = 'set_input_source {}'.format(source)
            self._source = source
            self._frequency = self.freq


        @property
        def pll(self):
            if isinstance(self.source, self._si._PLL):
                return self.source


        @property
        def freq(self):
            return math.floor(self.source.freq / self.divider)


        def set_frequency(self, freq):
            self._si._action = 'set_frequency {}'.format(freq)
            d = self.source.freq / freq
            self._set_divider(d)
            self._frequency = freq
            return True


        def restore_frequency(self):
            self._si._action = 'restore_frequency'
            self.set_frequency(self._frequency)


        @property
        def divider(self):
            return self._divider


        @property
        def is_in_integer_mode(self):
            raise NotImplementedError()


        def _set_divider(self, divider):
            # MS6 and MS7 are integer-only dividers. The valid range
            # of values for these dividers is all even integers between 6 and 254 inclusive.
            # For MS6 and MS7, set MSx_P1 directly (e.g., MSx_P1=divide value).

            a, b, c, _is_even_integer = self._validate_divider(divider)

            p1 = 128 * a + math.floor(128 * b / c) - 512

            # p2 = 128 * b - c * math.floor(128 * b / c)
            # p2 = math.floor(128 * b - c * math.floor(128 * b / c))
            # p2 = math.floor(c * (128 * b / c) - c * math.floor(128 * b / c))
            p2 = math.floor(c * (128 * b / c - math.floor(128 * b / c)))

            p3 = c

            if self._idx in self.INTEGER_ONLY_MULTISYNTHS:
                p1 = a

            self._set_integer_mode(_is_even_integer)
            result = self._set_parameters(p1, p2, p3)
            self._post_set_divider()
            self._divider = divider
            return result


        def _validate_divider(self, divider):

            assert self.DIVIDER_MIN + 1 / self.DENOMINATOR_MAX <= divider <= self.DIVIDER_MAX, \
                'Must {} + 1 / ((2 ** {}) - 1) <=  ({})  <= {}'.format(self.DIVIDER_MIN,
                                                                       self.DENOMINATOR_BITS,
                                                                       divider,
                                                                       self.DIVIDER_MAX)
            a = math.floor(divider)
            b = math.floor(self.denominator_max * (divider - a))
            c = self.denominator_max  # vcxo and pll use different denominators to fill up P3 register value,

            _is_even_integer = self._is_even_integer(divider)

            return a, b, c, _is_even_integer


        def _is_even_integer(self, divider):
            d = math.floor(divider)
            return d == divider and d % 2 == 0


        def _set_integer_mode(self, value = True):
            raise NotImplementedError()


        def _set_parameters(self, p1, p2, p3):

            params = (p1, p2, p3)

            bits_8 = ((7, 0),)
            bits_18 = ((17, 16), (15, 8), (7, 0))
            bits_20 = ((19, 16), (15, 8), (7, 0))

            bits_ranges = {1: bits_8, 2: [], 3: []} if self._idx in self.INTEGER_ONLY_MULTISYNTHS else \
                {1: bits_18, 2: bits_20, 3: bits_20}

            for i in range(len(params)):
                param_idx = i + 1
                for bits_range in bits_ranges[param_idx]:
                    idx_msb, idx_lsb = bits_range
                    element_name = 'MS{}_P{}_{}_{}'.format(self.name, param_idx, idx_msb, idx_lsb)
                    self._si._write_element_by_name(element_name, _section_value(params[i], idx_msb, idx_lsb))

            return True


        def _post_set_divider(self):
            self._maintain_phase_offset()


        def _maintain_phase_offset(self):
            if self.pll:
                # https://groups.io/g/BITX20/topic/si5351a_facts_and_myths/5430607
                # need to reset PLL in order to synch phases of outputs.
                self.pll.reset()


    class _PLL(_MultisynthBase):

        NAMES = {'A': 0, 'B': 1}

        FREQ_INPUT_MIN = int(10e6)
        FREQ_INPUT_MAX = int(40e6)

        FREQ_VCO_MIN = int(600e6)
        FREQ_VCO_MAX = int(900e6)

        DIVIDER_MIN = 15
        DIVIDER_MAX = 90
        DIVIDER_DEFAULT = 36


        def __init__(self, si, name, xtal_as_source = True):
            self._name = name
            super().__init__(si, idx = self.NAMES[name])
            self._xtal_as_source = xtal_as_source
            self.init()


        def init(self):
            self._si._action = 'pll init.'
            self._set_divider(self.DIVIDER_DEFAULT)
            self.set_input_source(xtal_as_source = self._xtal_as_source)
            self.reset()  # reset after source set. https://groups.io/g/BITX20/topic/si5351a_facts_and_myths/5430607


        @property
        def name(self):
            return 'N' + self._name


        @property
        def freq(self):
            freq = math.floor(self.source.freq * self.divider)  # using "*", not "/" for PLL

            assert self.FREQ_VCO_MIN <= freq <= self.FREQ_VCO_MAX, 'Fvco must be between {:0.2e} ~ {:0.2e} Hz.'.format(
                self.FREQ_VCO_MIN, self.FREQ_VCO_MAX)

            return freq


        def set_frequency(self, freq):
            self._si._action = 'pll set frequency {}'.format(freq)
            d = freq / self.source.freq
            self._set_divider(d)
            self._frequency = self.freq  # validate FREQ_VCO_MIN <= freq <= FREQ_VCO_MAX
            # self._si.restore_clocks_freqs()  # adjust multisynches for each clocks. but it may be looping.
            return True


        def reset(self):
            self._si._action = 'reset pll {}'.format(self._idx)

            element_name = 'PLL{}_RST'.format(self._name)
            self._si._write_element_by_name(element_name, 1)

            self._si.map.elements[element_name]['element'].value = 0
            # This is a self clearing bit. I2C bus NAK if immediate read after reset.


        def set_input_source(self, xtal_as_source = True):
            self._si._action = 'pll set_input_source xtal_as_source = {}'.format(xtal_as_source)

            # If spread spectrum is not enabled, either of the two PLLs may be used as the source for any outputs of the
            # Si5351A.
            # If both XTAL and CLKIN input options are used simultaneously (Si5351C only), then one PLL must be
            # reserved for use with CLKIN and one for use with the XTAL.
            # Note: PLLA must be used for any spread spectrum-enabled outputs. PLLB must be used for any VCXO outputs.
            #
            # If a PLL needs to be synchronized to a CMOS clock, PLLx_SRC must be 1.
            # The input frequency range of the PLL is 10 to 40 MHz. If CLKIN is > 40 MHz,
            # the CLKIN input divider must be used to bring the PLL input within the 10–40 MHz range.
            # See CLKIN_DIV[1:0], register 15, bits [7:6].

            self._source = self._si.xtal if xtal_as_source else self._si.clkin

            assert self.FREQ_INPUT_MIN <= self.source.freq <= self.FREQ_INPUT_MAX, \
                'Must {} <= F_input <= {}, now is {}'.format(self.FREQ_INPUT_MIN, self.FREQ_INPUT_MAX,
                                                             self.source.freq)

            element_name = 'PLL{}_SRC'.format(self._name)
            self._si._write_element_by_name(element_name, 0 if xtal_as_source else 1)

            if not xtal_as_source:
                self._si.clkin._set_divider()

            self._frequency = self.freq  # validate FREQ_VCO_MIN <= freq <= FREQ_VCO_MAX


        @property
        def is_in_integer_mode(self):
            return self._si.map.elements['FB{}_INT'.format(self._name)]['element'].value == 1


        def _set_integer_mode(self, value = True):
            # If a + b/c is an even integer, integer mode may be enabled for PLLA or PLLB by setting parameter FBA_INT or
            # FBB_INT respectively. In most cases setting this bit will improve jitter when using even integer divide values.
            # Whenever spread spectrum is enabled, FBA_INT must be set to 0.

            self._si._write_element_by_name('FB{}_INT'.format(self._name), 1 if value else 0)


        def _post_set_divider(self):
            # https://www.silabs.com/content/usergenerated/asi/cloud/attachments/siliconlabs/en/community/groups/timing/knowledge-base/jcr:content/content/primary/blog/modifying_the_feedba-K8Pv/311668.pdf
            # https://groups.io/g/BITX20/topic/si5351a_facts_and_myths/5430607
            self.reset()


    class _Multisynth(_MultisynthBase):
        DIVIDER_MIN = 6
        DIVIDER_MAX = 2048
        DIVIDER_DEFAULT = 36
        DIVIDER_MIN_INTEGER_ONLY_MULTISYNTHS = 6
        DIVIDER_MAX_INTEGER_ONLY_MULTISYNTHS = 254


        def __init__(self, si, idx, pll = 'A'):
            super().__init__(si, idx)
            self.set_input_source(pll = pll)


        @property
        def status(self):
            # status = super().status  # doesn't work in uPy
            status = OrderedDict({'type'       : self.__class__.__name__,
                                  'idx'        : self._idx,
                                  'source_type': self.source.__class__.__name__,
                                  'source_idx' : self.source._idx,
                                  'source_freq': self.source.freq,
                                  'my_freq'    : self.freq,
                                  'my_divider' : self.divider})

            status.update({'is_in_integer_mode': self.is_in_integer_mode,
                           'is_divided_by_4'   : self.is_divided_by_4})
            return status


        def set_input_source(self, pll = 'A'):
            self._si._action = 'multisynth set_input_source PLL {}'.format(pll)

            # Each of these dividers can be set to use PLLA or PLLB as its reference by setting MSx_SRC to 0 or 1 respectively.
            # See bit 5 description of registers 16-23.

            valids = self._si._PLL.NAMES.keys()
            assert pll in valids, 'valid PLL: {}'.format(valids)

            self._source = self._si.plls[pll]
            self._frequency = self.freq
            self._si._write_element_by_name('MS{}_SRC'.format(self._idx), self._si._PLL.NAMES[pll])


        def enable_fanout(self, value = True):
            self._si._action = 'multisynth enable_fanout {}'.format(value)
            self._si._write_element_by_name('MS_FANOUT_EN', 1 if value else 0)


        def _validate_divider(self, divider):
            a, b, c, _is_even_integer = super()._validate_divider(divider)

            if self._idx in self.INTEGER_ONLY_MULTISYNTHS:
                assert _is_even_integer and (self.DIVIDER_MIN_INTEGER_ONLY_MULTISYNTHS <= divider <=
                                             self.DIVIDER_MAX_INTEGER_ONLY_MULTISYNTHS), \
                    'Multisynth {} divider validation error: "a + b/c" ({:0.4f}) must be an even integer and  ({} <= a <= {})'.format(
                        self._idx, divider,
                        self.DIVIDER_MIN_INTEGER_ONLY_MULTISYNTHS,
                        self.DIVIDER_MAX_INTEGER_ONLY_MULTISYNTHS)

            return a, b, c, _is_even_integer


        @property
        def is_in_integer_mode(self):
            if self._idx in self.INTEGER_ONLY_MULTISYNTHS:
                return True
            if self._idx in range(self.N_HIGH_FREQUENCY_MULTISYNTHS):
                return self._si.map.elements['MS{}_INT'.format(self._idx)]['element'].value == 1
            return False


        def _set_integer_mode(self, value = True):
            if self._idx not in self.INTEGER_ONLY_MULTISYNTHS:
                self._si._write_element_by_name('MS{}_INT'.format(self._idx), 1 if value else 0)


        @property
        def is_divided_by_4(self):
            if self._idx in range(self.N_HIGH_FREQUENCY_MULTISYNTHS):
                return self._si.map.elements['MS{}_DIVBY4'.format(self._idx)]['element'].value == 0x03
            return False


        def _set_divided_by_4(self, value = True):

            # Output frequencies greater than 150 MHz are available on Multisynths 0-5. For this frequency range a divide value
            # of 4 must be used by setting
            # MSx_P1=0,
            # MSx_P2=0,
            # MSx_P3=1,
            # MSx_INT=1, and
            # MSx_DIVBY4[1:0]=11b.
            # Set the appropriate feedback Multisynth to generate fVCO=Fout*4.

            assert self._idx in range(
                self.N_HIGH_FREQUENCY_MULTISYNTHS), 'High frequencies only for multisynths 0-5'

            if value:
                self._set_parameters(p1 = 0, p2 = 0, p3 = self.denominator_max)
                self._set_integer_mode(True)
                self._divider = 4
            self._si._write_element_by_name('MS{}_DIVBY4'.format(self._idx), 0x03 if value else 0x00)

            self._post_set_divider()


    class _Clock(_MultisynthBase):

        DIVIDER_MIN = 1
        DIVIDER_MAX = 128
        DIVIDER_DEFAULT = 1

        CLOCK_SOURCEs = {'XTAL': 0x00, 'CLKIN': 0x01, 'Group_MultiSynth': 0x2, 'MultiSynth': 0x3}
        OUTPUT_STRENGTHs = {2: 0x00, 4: 0x01, 6: 0x02, 8: 0x03}
        DISABLE_STATEs = {'LOW': 0x00, 'HIGH': 0x01, 'HIGH_IMPEDANCE': 0x02, 'NEVER_DISABLED': 0x03}
        R_DIVIDERs = {1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6, 128: 7}


        def __init__(self, si, idx,
                     freq = None,
                     source = 'MultiSynth',
                     strength_mA = 8,
                     disable_state = 'LOW'):

            super().__init__(si, idx)
            self._set_strength(strength_mA)
            self._set_disable_state(disable_state)
            self.set_input_source(source)
            self.set_frequency(self._si.FREQ_REF if freq is None else freq)
            self.set_phase(PHASE_DEFAULT)


        @property
        def status(self):
            # status = super().status  # doesn't work in uPy
            status = OrderedDict({'type'       : self.__class__.__name__,
                                  'idx'        : self._idx,
                                  'source_type': self.source.__class__.__name__,
                                  'source_idx' : self.source._idx,
                                  'source_freq': self.source.freq,
                                  'my_freq'    : self.freq,
                                  'my_divider' : self.divider})

            status.update({'power_downed'        : self.power_downed,
                           'enabled'             : self.enabled,
                           'oeb_pin_masked'      : self.oeb_pin_masked,
                           'phase_offset_enabled': self.phase_offset_enabled,
                           'phase'               : self.phase if self.phase_offset_enabled else 0})
            return status


        def set_input_source(self, source = 'MultiSynth'):
            self._si._action = 'set_input_source {}'.format(source)

            # Generally, Multisynth x should be output on CLKx, however XO, CLKIN, or a divided version of either (see section
            # 4.2.2 on R dividers) may also be output on each of the CLKx pins. Additionally, MS0 (or a divided version of MS0)
            # may be output on CLK0-CLK3, and MS4 (or a divided version of MS4) may be output on CLK4-CLK7. See
            # CLKx_SRC description for details.

            valids = self.CLOCK_SOURCEs.keys()
            assert source in valids, 'valid source: {}'.format(valids)

            self._source = {'XTAL'            : self._si.xtal,
                            'CLKIN'           : self._si.clkin,
                            'Group_MultiSynth': self._si.multisynths[self._idx // 4],
                            'MultiSynth'      : self._si.multisynths[self._idx]}[source]

            self._frequency = self.freq
            self._si._write_element_by_name('CLK{}_SRC'.format(self._idx), self.CLOCK_SOURCEs[source])


        @property
        def multisynth(self):
            if isinstance(self.source, self._si._Multisynth):
                return self.source


        @property
        def pll(self):
            if self.multisynth:
                if isinstance(self.multisynth.source, self._si._PLL):
                    return self.multisynth.source


        def set_frequency(self, freq, can_tune_pll = True):
            self._si._action = 'set_frequency {}'.format(freq)

            if self.pll is not None:  # source with adjustable frequency
                if freq * self.multisynth.DIVIDER_MIN * min(self.R_DIVIDERs.keys()) > self.pll.FREQ_VCO_MAX:
                    # high frequency, need to use 4 as divider and adjust PLL's frequency.
                    self.pll.set_frequency(freq * 4)  # divider is fixed, so the fvco of PLL must be adjusted.
                    self.multisynth._set_divided_by_4(True)
                    self._frequency = freq
                    return True

                else:  # divided by 4 is not necessary
                    if self.multisynth.is_divided_by_4:  # change mode.
                        self.multisynth._set_divided_by_4(False)

                    # if current PLL's frequency needs to be adjusted.
                    if can_tune_pll:
                        if self.pll.freq / (self.multisynth.DIVIDER_MAX * max(self.R_DIVIDERs.keys())) > freq:
                            self.pll.set_frequency(self.pll.FREQ_VCO_MIN)
                        if self.pll.freq / (self.multisynth.DIVIDER_MIN * min(self.R_DIVIDERs.keys())) < freq:
                            self.pll.set_frequency(self.pll.FREQ_VCO_MAX)

                    # try setting divider and therefore frequency
                    for d in sorted(self.R_DIVIDERs.keys()):
                        if math.floor(self.multisynth.freq / d) == math.floor(freq):  # match, do it within R.
                            self._set_divider(d)
                            self._frequency = freq
                            return True

                        else:  # need to adjust multisynth frequency.
                            try:  # try adjusting multisynth frequency.
                                if self.multisynth.set_frequency(freq * d) is True:
                                    self._set_divider(d)  # source can provide the desired freq, adjust R divider again.
                                    self._frequency = freq
                                    return True

                            except AssertionError as e:
                                print('Failed in setting multisynth {} to freq {} x {} = {}.'.format(
                                    self.multisynth._idx, freq, d, freq * d))

            else:  # source (Xtalk, Clkin) with fixed frequency
                for d in self.R_DIVIDERs.keys():
                    if math.floor(self.source.freq / d) == math.floor(freq):
                        self._set_divider(d)
                        self._frequency = freq
                        return True

            raise ValueError('Clock {} failed in setting frequency as {}.'.format(self._idx, freq))


        def restore_frequency(self, can_tune_pll = True):
            self._si._action = 'restore_frequency'
            self.set_frequency(self._frequency, can_tune_pll = can_tune_pll)


        @property
        def enabled(self):
            return self._si.map.elements['CLK{}_OEB'.format(self._idx)]['element'].value == 0


        def enable(self, value = True):
            if not self.power_downed:  # can't enable/disable if power downed.
                self._si._action = 'enable_output_clock {} {}'.format(self._idx, value)
                self._si._write_element_by_name('CLK{}_OEB'.format(self._idx), 0 if value else 1)


        @property
        def power_downed(self):
            return self._si.map.elements['CLK{}_PDN'.format(self._idx)]['element'].value == 1


        def power_down(self, value = True):
            self._si._action = 'power_down {}'.format(value)

            if value:
                self.enable(False)  # disable before power down.

            self._si._write_element_by_name('CLK{}_PDN'.format(self._idx), 1 if value else 0)

            if not value:  # https://groups.io/g/BITX20/topic/si5351a_facts_and_myths/5430607
                self._maintain_phase_offset()


        @property
        def oeb_pin_masked(self):
            return self._si.map.elements['OEB_MASK_{}'.format(self._idx)]['element'].value == 1


        @property
        def is_in_integer_mode(self):
            return True


        def _set_strength(self, mA = 8):
            valids = self.OUTPUT_STRENGTHs.keys()
            assert mA in valids, 'valid mA: {}'.format(valids)

            self._si._write_element_by_name('CLK{}_IDRV'.format(self._idx), self.OUTPUT_STRENGTHs[mA])


        def _set_invert(self, value = True):
            self._si._write_element_by_name('CLK{}_INV'.format(self._idx), 1 if value else 0)


        def _mask_oeb_pin(self, value = True):
            self._si._write_element_by_name('OEB_MASK_{}'.format(self._idx), 1 if value else 0)


        def _set_disable_state(self, state = 'LOW'):
            valids = self.DISABLE_STATEs.keys()
            assert state in valids, 'valid states: {}'.format(valids)

            self._si._write_element_by_name('CLK{}_DIS_STATE'.format(self._idx), self.DISABLE_STATEs[state])


        def _set_divider(self, divider = 1):

            # The R dividers can be used to generate frequencies below about 500 kHz. Each individual output R divider can be
            # set to 1, 2, 4, 8,....128 by writing the proper setting for Rx_DIV. Set this parameter to generate frequencies down to
            # 8kHz

            valids = self.R_DIVIDERs.keys()
            assert divider in valids, 'valid divider: {}'.format(valids)

            self._divider = divider
            self._si._write_element_by_name('R{}_DIV'.format(self._idx), self.R_DIVIDERs[divider])


        @property
        def phase_offset_enabled(self):
            if self._idx in range(self.N_MULTISYNTHS_WITH_OUTPUT_SKEW):
                return self._si.map.elements['CLK{}_PHOFF'.format(self._idx)]['element'].value != 0
            return False


        def set_phase(self, phase):
            self._action = 'set_phase {} idx {}'.format(phase, self._idx)

            # Set offset_seconds = 0 to disable it.
            #
            # It's important to note that Multisynth integer mode cannot be used when adding phase offsets in NVM. In
            # other words, MSx_INT needs to be set to 0 if phase offsets need to be enabled.
            #
            #   Outputs 0-5 of the Si5351 can be programmed with an independent initial phase offset. The phase offset only
            # works when MS0-5 are set as fractional dividers (divider values greater than 8). The phase offset parameter is an
            # unsigned integer where each LSB represents a phase difference of a quarter of the VCO period, TVCO/4. Use the
            # equation below to determine the register value. Also, remember that any divider using the phase offset feature
            # needs the MSx_INT bit set to 0.
            #
            # CLKx_PHOFF[4:0] = Round(DesiredOffset(sec) * 4 * FVCO)
            # ==> typo, should be [6:0]

            if self._idx in range(self.N_MULTISYNTHS_WITH_OUTPUT_SKEW) and self.multisynth is not None:

                cycle = (phase % DEGREES_IN_PI2) / DEGREES_IN_PI2
                freq_vco = self.pll.freq  # PLL

                freq_min = cycle * freq_vco * 4 / (2 ** 7 - 0.5)  # CLKx_PHOFF has 7 bits, must < 128 after rounded.
                assert self.freq > freq_min, \
                    'my freq must be greater than {:0.3e} to have {} degree phase offset.'.format(freq_min, phase)

                my_period = 1 / self.freq
                offset_seconds = cycle * my_period
                offset = int(round(offset_seconds * 4 * freq_vco))
                self._set_phase_offset(offset)

                if phase != 0:
                    self.multisynth._set_integer_mode(False)
                else:
                    self.multisynth.restore_frequency()  # restore integer mode if applicable.

                self._maintain_phase_offset()  # need to reset PLL


        @property
        def phase_offset(self):
            if self._idx in range(self.N_MULTISYNTHS_WITH_OUTPUT_SKEW) and self.multisynth is not None:
                return self._si.map.elements['CLK{}_PHOFF'.format(self._idx)]['element'].value
            return 0


        @property
        def phase(self):
            my_period = 1 / self.freq
            freq_vco = self.pll.freq  # PLL
            offset_seconds = self.phase_offset / (4 * freq_vco)
            phase = offset_seconds / my_period * DEGREES_IN_PI2 % DEGREES_IN_PI2
            return phase


        def _set_phase_offset(self, offset = 0):
            # CLKx_PHOFF[6:0] is an unsigned integer with one LSB equivalent to a time delay of
            # Tvco/4, where Tvco is the period of the VCO/PLL associated with this output.

            # assert 0 <= offset < 2 ** 7, 'offset ({}) should be less than 128.'.format(offset)

            self._si._write_element_by_name('CLK{}_PHOFF'.format(self._idx), offset & 0x7F)


    class _CLK(_MultisynthBase):

        DIVIDER_DEFAULT = 1


        def __init__(self, si, freq):
            self.set_frequency(freq)
            super().__init__(si, idx = 0)
            self.set_input_source()
            self.enable_fanout(True)


        @property
        def status(self):
            return OrderedDict({'type'   : self.__class__.__name__,
                                'idx'    : self._idx,
                                'my_freq': self.freq})


        @property
        def freq(self):
            return math.floor(self._freq / self.divider)


        def set_frequency(self, freq):
            self._frequency = self._freq = freq


        def set_input_source(self):
            self._source = None


        def enable_fanout(self, value = True):
            pass


        @property
        def is_in_integer_mode(self):
            return True


        def _set_divider(self, _ = None):
            self._divider = 1


        # ========= not used inherited ============================

        @property
        def pll(self):
            raise NotImplementedError()


        def _set_parameters(self, p1, p2, p3):
            raise NotImplementedError()


        def _validate_divider(self, divider):
            raise NotImplementedError()


        def _is_even_integer(self, divider):
            raise NotImplementedError()


        def _set_integer_mode(self, value = True):
            raise NotImplementedError()


    class _Xtal(_CLK):

        CRYSTAL_INTERNAL_LOAD_CAPACITANCEs = {6: 0x01, 8: 0x02, 10: 0x03}


        def __init__(self, si, freq, pF = 10):
            super().__init__(si, freq = freq)
            self.set_internal_load_capacitance(pF = pF)


        def set_internal_load_capacitance(self, pF = 10):
            self._si._action = 'set_internal_load_capacitance {}'.format(pF)

            # If the source for the PLL is a crystal, PLLx_SRC must be set to 0 in register 15. XTAL_CL[1:0] must also be set to
            # match the crystal load capacitance (see register 183).

            valids = self.CRYSTAL_INTERNAL_LOAD_CAPACITANCEs.keys()
            assert pF in valids, 'valid pF: {}'.format(valids)

            self._si._write_element_by_name('XTAL_CL', self.CRYSTAL_INTERNAL_LOAD_CAPACITANCEs[pF])


        def enable_fanout(self, value = True):
            self._si._action = 'Xtal enable_fanout {}'.format(value)
            self._si._write_element_by_name('XO_FANOUT_EN', 1 if value else 0)


    def __init__(self, i2c = None, i2c_address = I2C_ADDRESS, pin_oeb = None, pin_ssen = None,
                 n_channels = None, channels_in_use = None,
                 freq_xtal = FREQ_REF, freq_clkin = FREQ_REF, freq_vcxo = FREQ_REF,
                 registers_map = None, registers_values = None,
                 commands = None):

        registers_map = _get_registers_map() if registers_map is None else registers_map

        super().__init__(n_channels = self.N_OUTPUT_CLOCKS if n_channels is None else n_channels,
                         freq_mclk = freq_xtal,
                         registers_map = registers_map, registers_values = registers_values,
                         commands = commands)

        self._i2c = I2C(i2c, i2c_address)
        self._pin_oeb = pin_oeb
        self._pin_ssen = pin_ssen

        self.channels_in_use = self.OUTPUT_CLOCKS_IN_USE if channels_in_use is None else channels_in_use
        self._current_channel_idx = 0

        self._freq_xtal = freq_xtal
        self._freq_clkin = freq_clkin
        self._freq_vcxo = freq_vcxo

        self.init()


    def _build(self):
        self.interrupts = self._Interrupts(self)
        self.xtal = self._Xtal(self, self._freq_xtal)
        self.clkin = self.xtal
        self.plls = {name: self._PLL(self, name = name) for name in self._PLL.NAMES.keys()}
        self.multisynths = [self._Multisynth(self, i) for i in range(self.n_channels)]
        self.clocks = [self._Clock(self, i) for i in range(self.n_channels)]


    def init(self):
        self._action = 'init'
        self._build()
        self._power_down_all_outputs(True)

        # step 4: define inputs and features
        #     input mode
        #         mode enable/disable
        # self.enable(False)

        #         frequency 25/27 MHz
        #         internal load 0/6/8/10 pF
        # self.xtal.set_internal_load_capacitance(pF = 8)

        #     Feature
        #         Spread Spectrum Clock Config
        #             enable True/False
        # self.spread_spectrum.enable(False)

        #             direction down/center
        #             amplitude 0.1%
        # step 5: define output frequencies
        #     Out0
        #         mode enabled/disabled/unused
        # self.clocks[0].enable()

        #         frequency ??? Hz (ex. 19.2MHz, 2*IN0, OUT5, OUT5 + 5ppb)
        # self.clocks[0].set_frequency(25e6)

        #         feature SSC
        # self.spread_spectrum.enable(False)

        #     Out1
        #     ...
        # step 6: define output skews
        #     Out0
        #         desired skew 6ns  ==> Actual_Skew = 6.127ns,  CLK0_PHOFF = 0x16
        # self.clocks[0].set_phase_offset(6.127e-9)

        #     Out1
        #     ...
        # step 7: define output driver configuration
        #     Out1
        #         format driver_strength 2/4/6/8mA
        # self.clocks[0]._set_strength(8)

        #         disable state stop_low/stop_high/HiZ
        # self.clocks[0]._set_disable_state('LOW')

        for i in self.channels_in_use:
            self.clocks[i].power_down(False)  # Just power up clocks in use.

        self.start()
        self.reset_plls()


    def reset_plls(self):
        self._action = 'reset_plls'
        self._write_register_by_name('PLL_Reset', 0xA0)

        self.map.registers['PLL_Reset'].reset()
        # Synch. This are self clearing bits. I2C bus NAK if immediate read after reset.


    def enable(self, value = True):
        self.enable_output(value)


    def enable_output(self, value = True):  # enable only
        self._action = 'enable_output: {}'.format(value)
        self._enable_all_outputs(value)


    def enable_output_channel(self, idx, value = True):
        self._action = 'enable_output_channel: {} {}'.format(idx, value)
        self.clocks[idx].enable(value)


    def set_frequency(self, freq, idx = None):
        if idx is not None:
            self._current_channel_idx = idx
        self._action = 'set_frequency {} idx {}'.format(freq, self._current_channel_idx)
        self.clocks[self._current_channel_idx].set_frequency(freq)


    def set_phase(self, phase, idx = None):
        if idx is not None:
            self._current_channel_idx = idx
        self._action = 'set_phase {} idx {}'.format(phase, self._current_channel_idx)
        self.clocks[self._current_channel_idx].set_phase(phase)


    def restore_clocks_freqs(self, can_tune_pll = True):
        self._action = 'restore_clocks_freqs'
        for clk in self.clocks:
            if not clk.power_downed:
                try:
                    clk.restore_frequency(can_tune_pll = can_tune_pll)
                except AssertionError as e:
                    print(e)


    def find_integer_dividers(self, freq_desired, even_only = True, torance_hz = 1, freq_ref = FREQ_REF):

        # hierachy structure
        xtal = self._Xtal(self, freq_ref)
        pll = self._PLL(self, 'A')
        multisynth = self._Multisynth(self, 0)
        clock = self._Clock(self, 0)

        pll._source = xtal
        multisynth._source = pll
        clock._source = multisynth

        # possible dividers
        divider_plls = range(pll.DIVIDER_MIN, pll.DIVIDER_MAX + 1)
        divider_multisynths = range(multisynth.DIVIDER_MIN, multisynth.DIVIDER_MAX + 1)
        divider_rs = list(self._Clock.R_DIVIDERs.keys())

        results = []

        for dp in divider_plls:
            for dm in divider_multisynths:
                for dr in divider_rs:
                    try:
                        if even_only:
                            assert dp % 2 == 0 and dm % 2 == 0

                        pll._divider = dp
                        multisynth._divider = dm
                        clock._divider = dr

                        freq_clock = clock.freq  # validate
                        diff = abs(freq_clock - freq_desired)

                        if diff < torance_hz:
                            match = ((dp, dm, dr), (xtal.freq, pll.freq, multisynth.freq, clock.freq))
                            results.append(match)
                    except:
                        pass
        return results


    def find_integer_pll_dividers_for_clocks(self, desired_clock_freqs, *args, **kwargs):
        freqs_matches = [self.find_integer_dividers(freq, *args, **kwargs) for freq in desired_clock_freqs]
        freqs_pll_dividers = [set([row[0][0] for row in freq_matches]) for freq_matches in freqs_matches]
        common_pll_dividers = set.intersection(*freqs_pll_dividers)
        return common_pll_dividers, freqs_pll_dividers, freqs_matches


    @property
    def registers_values(self):
        return self.map.addressed_values


    @property
    def revision(self):
        if not self.is_virtual_device:
            return self.status.elements['REVID'].value
        return 0


    @property
    def status(self):
        return self._read_register_by_name('Device_Status')


    @property
    def current_configuration(self):
        import pandas as pd

        df_clkin = pd.DataFrame([self.clkin.status])
        df_xtal = pd.DataFrame([self.xtal.status])
        df_plls = pd.DataFrame([self.plls[i].status for i in self._PLL.NAMES.keys()])
        df_multisynths = pd.DataFrame([self.multisynths[i].status for i in range(self.n_channels)])
        df_clocks = pd.DataFrame([self.clocks[i].status for i in range(self.n_channels)])

        df = pd.merge(df_xtal, df_plls, how = 'outer',
                      left_on = ['type', 'idx'], right_on = ['source_type', 'source_idx'],
                      suffixes = ('_xtal', '_pll'))
        df.drop(columns = ['source_type', 'source_idx', 'source_freq'], inplace = True)

        df = pd.merge(df, df_multisynths, how = 'outer',
                      left_on = ['type_pll', 'idx_pll'], right_on = ['source_type', 'source_idx'],
                      suffixes = ('_pll', '_multisynth'))
        df.drop(columns = ['source_type', 'source_idx', 'source_freq'], inplace = True)

        df = pd.merge(df, df_clocks, how = 'outer',
                      left_on = ['type', 'idx'], right_on = ['source_type', 'source_idx'],
                      suffixes = ('_multisynth', '_clock'))
        df.drop(columns = ['type_pll', 'type_multisynth', 'type_clock', 'source_type', 'source_idx', 'source_freq'],
                inplace = True)

        df.columns = ['mclk_type', 'mclk_idx', 'mclk_freq', 'pll_idx', 'pll_freq', 'pll_divider', 'multisynth_idx',
                      'multisynth_freq', 'multisynth_divider', 'multisynth_in_integer_mode', 'multisynth_divided_by_4',
                      'clock_idx', 'clock_freq', 'clock_divider', 'power_downed', 'enabled', 'oeb_pin_masked',
                      'phase_offset_enabled', 'phase']

        df = df.reindex(
            columns = ['mclk_type', 'mclk_idx', 'mclk_freq', 'pll_idx', 'pll_divider', 'pll_freq', 'multisynth_idx',
                       'multisynth_divider', 'multisynth_freq', 'multisynth_in_integer_mode', 'multisynth_divided_by_4',
                       'clock_idx', 'clock_divider', 'clock_freq', 'power_downed', 'enabled', 'oeb_pin_masked',
                       'phase_offset_enabled', 'phase'])
        return df


    @property
    def ready(self):
        if not self.is_virtual_device:
            return self.status.elements['SYS_INIT'].value == 0
        return True


    @property
    def is_virtual_device(self):
        return self._i2c._i2c is None


    # =================================================================

    def _enable_all_outputs(self, value = True):
        for i in range(self.n_channels):
            self.clocks[i].enable(value)


    def _power_down_all_outputs(self, value = True):
        for i in range(self.n_channels):
            self.clocks[i].power_down(value)


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
