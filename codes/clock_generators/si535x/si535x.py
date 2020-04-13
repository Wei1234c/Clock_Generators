# https://www.silabs.com/documents/public/data-sheets/Si5351-B.pdf
# https://www.silabs.com/documents/public/application-notes/AN619.pdf


from .registers_map import _get_registers_map


try:
    from ..interfaces import *
    from utilities.adapters.peripherals import I2C
except:
    from interfaces import *
    from peripherals import I2C



class Si535x(Device):
    I2C_ADDRESS = 0x60
    FREQ_MCLK = int(25e6)
    N_OUTPUT_CLOCKS = 8
    N_USED_OUTPUT_CLOCKS = 3
    PLLs = ('A', 'B')
    N_PLLS = len(PLLs)
    DENOMINATOR_BITS = 20
    POW_2_DENOMINATOR_BITS = 2 ** DENOMINATOR_BITS - 1
    READ_ONLY_REGISTERS = (0,)
    INTEGER_ONLY_MULTISYNTHES = (6, 7)

    CLKIN_DIVIDERS = {1: 0x00, 2: 0x01, 4: 0x20, 8: 0x03}
    CLOCK_SOURCEs = {'XTAL': 0x00, 'CLKIN': 0x01, 'Group_MultiSynth': 0x2, 'MultiSynth': 0x3}
    OUTPUT_STRENGTHs = {2: 0x00, 4: 0x01, 6: 0x02, 8: 0x03}
    CRYSTAL_INTERNAL_LOAD_CAPACITANCEs = {6: 0x01, 8: 0x02, 10: 0x03}
    DISABLE_STATEs = {'LOW': 0x00, 'HIGH': 0x01, 'HIGH_IMPEDANCE': 0x02, 'NEVER_DISABLED': 0x03}
    R_DIVIDERs = {1: 0, 2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6, 128: 7}


    class _Interrupts:

        def __init__(self, si):
            self._si = si
            self.set_masks(0)
            self.clear_stickys()


        @property
        def masks(self):
            return self._si._read_register_by_name('Interrupt_Status_Mask')


        def set_masks(self, mask = 0x00):
            self._si._write_register_by_name('Interrupt_Status_Mask', mask)


        def set_mask(self, interrupt_name, value = True):
            valids = self._si.map.registers['Interrupt_Status_Mask'].elements.keys()
            assert interrupt_name in valids, 'valid names: {}'.format(valids)
            self._si._write_element_by_name('{}_MASK'.format(interrupt_name.upper()), 1 if value else 0)


        @property
        def stickys(self):
            return self._si._read_register_by_name('Interrupt_Status_Sticky')


        def clear_stickys(self):
            self._si._write_register_by_name('Interrupt_Status_Sticky', 0x00)


        def clear_sticky(self, interrupt_name):
            valids = self._si.map.registers['Interrupt_Status_Sticky'].elements.keys()
            assert interrupt_name in valids, 'valid names: {}'.format(valids)
            self._si._write_element_by_name('{}_STKY'.format(interrupt_name.upper()), 0)


    class _MultisynthBase:
        DIVIDER_MIN = None
        DIVIDER_MAX = None


        def __init__(self, si, idx):
            self._si = si
            self._idx = idx
            self._name = str(idx)
            self._divider = self.DIVIDER_MAX
            self._source = None
            # self.set_input_source()  # need implement


        @property
        def source(self):
            return self._source


        def set_input_source(self, source):
            self._source = source
            self._frequency = math.floor(self.source.freq / self.divider)


        @property
        def freq(self):
            return math.floor(self.source.freq / self.divider)


        def set_frequency(self, freq):
            d = self.source.freq / freq
            a = int(d)
            b = (d - a) * self._si.POW_2_DENOMINATOR_BITS
            c = self._si.POW_2_DENOMINATOR_BITS
            self._set_divider(a, b, c)
            self._frequency = freq
            return True


        def restore_frequency(self, ):
            self.set_frequency(self._frequency)


        @property
        def divider(self):
            return self._divider


        def _set_divider(self, a, b = 0, c = 1):
            """
             MS6 and MS7 are integer-only dividers. The valid range
            of values for these dividers is all even integers between 6 and 254 inclusive.
            For MS6 and MS7, set MSx_P1 directly (e.g., MSx_P1=divide value).
            """
            a, b, c, _is_even_integer = self._validate_abc(a, b, c)
            self._divider = a + b / c

            if _is_even_integer:
                self._set_integer_mode(True)
                p1 = a if self._idx in self._si.INTEGER_ONLY_MULTISYNTHES else 128 * a + math.floor(128 * b / c) - 512
                p2 = 0
                p3 = 1
            else:
                self._set_integer_mode(False)
                p1 = 128 * a + math.floor(128 * b / c) - 512
                p2 = 128 * b - c * math.floor(128 * b / c)
                p3 = c

            return self._set_parameters(p1, p2, p3)


        def _set_integer_mode(self, value = True):
            raise NotImplementedError()


        def _set_parameters(self, p1, p2 = None, p3 = None):
            params = (p1, p2, p3)

            bits_8 = ((7, 0),)
            bits_18 = ((17, 16), (15, 8), (7, 0))
            bits_20 = ((19, 16), (15, 8), (7, 0))

            bits_ranges = {1: bits_8, 2: [], 3: []} if self._idx in self._si.INTEGER_ONLY_MULTISYNTHES else \
                {1: bits_18, 2: bits_20, 3: bits_20}

            for i in range(len(params)):
                param_idx = i + 1
                for bits_range in bits_ranges[param_idx]:
                    element_name = 'MS{}_P{}_{}_{}'.format(self._name, param_idx, bits_range[0], bits_range[1])
                    mask = (2 ** (bits_range[0] - bits_range[1] + 1) - 1) << bits_range[1]
                    value = (params[i] & mask) >> bits_range[1]
                    self._si._write_element_by_name(element_name, value)

            return True


        def _validate_abc(self, a, b, c):
            a = int(a)
            b = int(b)
            c = int(c)
            _is_even_integer = self._is_abc_even_integer(a, b, c)

            return a, b, c, _is_even_integer


        def _is_abc_even_integer(self, a, b, c):
            return int(a) % 2 == 0 and b == 0 and c > 0


    class _Multisynth(_MultisynthBase):
        DIVIDER_MIN = 8
        DIVIDER_MAX = 2048


        def __init__(self, si, idx):
            super().__init__(si, idx)
            self.set_input_source(pll_idx = 0)
            self.enable_fanout(True)


        def set_input_source(self, pll_idx = 0):
            """
            Each of these dividers can be set to use PLLA or PLLB as its reference by setting MSx_SRC to 0 or 1 respectively.
            See bit 5 description of registers 16-23.
            """
            valids = range(self._si.N_PLLS)
            assert pll_idx in valids, 'valid pll_idx: {}'.format(valids)

            self._source = self._si.plls[pll_idx]
            self._frequency = math.floor(self.source.freq / self.divider)
            self._si._write_element_by_name('MS{}_SRC'.format(self._idx), pll_idx)


        def enable_fanout(self, value = True):
            self._si._write_element_by_name('MS_FANOUT_EN', 1 if value else 0)


        def _validate_abc(self, a, b, c):
            a = int(a)
            b = int(b)
            c = int(c)
            _is_even_integer = self._is_abc_even_integer(a, b, c)

            if self._idx in self._si.INTEGER_ONLY_MULTISYNTHES:
                assert _is_even_integer and (6 <= a <= 254), \
                    '"a" must be an even integer and  (6 <= a <= 254)'
                b = 0
                c = 1
            else:
                assert self.DIVIDER_MIN + 1 / (self._si.POW_2_DENOMINATOR_BITS - 1) <= (a + b / c) <= self.DIVIDER_MAX, \
                    'Must {} + 1 / ((2 ** {}) - 1) <=  (a + b / c)  <= {}'.format(self.DIVIDER_MIN,
                                                                                  self._si.DENOMINATOR_BITS,
                                                                                  self.DIVIDER_MAX)

            return a, b, c, _is_even_integer


        def _set_integer_mode(self, value = True):
            if self._idx not in self._si.INTEGER_ONLY_MULTISYNTHES:
                self._si._write_element_by_name('MS{}_INT'.format(self._idx), 1 if value else 0)


        def _set_divided_by_4(self, value = True):
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
            assert self._idx not in self._si.INTEGER_ONLY_MULTISYNTHES, \
                'Output frequencies greater than 150 MHz are available only on Multisynths 0-5.'

            if value:
                self._set_parameters(p1 = 0, p2 = 0, p3 = 1)
                self._set_integer_mode(True)
            self._si._write_element_by_name('MS{}_DIVBY4'.format(self._idx), 0x03 if value else 0x00)


    class _CLKIN:

        def __init__(self, si, freq = None):
            self._si = si
            self._freq = freq
            self._divider = 1
            self.enable_fanout(True)


        @property
        def freq(self):
            return math.floor(self._freq / self.divider)


        @property
        def divider(self):
            return self._divider


        def _set_divider(self):
            for d in sorted(self._si.CLKIN_DIVIDERS.keys()):
                if self._freq / d <= 40e6:
                    break
            assert 10e6 <= self._freq / d <= 40e6, 'The input frequency range of the PLLis 10 to 40 MHz'
            self._divider = d
            self._si._write_element_by_name('CLKIN_DIV', self._si.CLKIN_DIVIDERS[d])


        def enable_fanout(self, value = True):
            self._si._write_element_by_name('CLKIN_FANOUT_EN', 1 if value else 0)


    class _Xtal:

        def __init__(self, si, freq = None):
            self._si = si
            self.freq = freq
            self.set_internal_load_capacitance(pF = 10)
            self.enable_fanout(True)


        def set_internal_load_capacitance(self, pF = 10):
            """
            If the source for the PLL is a crystal, PLLx_SRC must be set to 0 in register 15. XTAL_CL[1:0] must also be set to
            match the crystal load capacitance (see register 183).
            """
            valids = self._si.CRYSTAL_INTERNAL_LOAD_CAPACITANCEs.keys()
            assert pF in valids, 'valid pF: {}'.format(valids)
            self._si._write_element_by_name('XTAL_CL', self._si.CRYSTAL_INTERNAL_LOAD_CAPACITANCEs[pF])


        def enable_fanout(self, value = True):
            self._si._write_element_by_name('XO_FANOUT_EN', 1 if value else 0)


    class _VCXO:

        def __init__(self, si, freq = None):
            self._si = si
            self.freq = freq


        # def get_freq_vco_xtal(self, freq_xtal, a, b, c):
        #     return freq_xtal * (a + b / c)
        #
        #
        # def get_freq_vco_clkin(self, freq_clkin, clkin_div, a, b, c):
        #     return freq_clkin / clkin_div * (a + b / c)

        def _set_paramenters(self, a, b, apr = 30):
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


    class _PLL(_MultisynthBase):
        FREQ_VCO_MIN = int(600e6)
        FREQ_VCO_MAX = int(900e6)
        DIVIDER_MIN = 15
        DIVIDER_MAX = 90
        DEFAULT_FVCO = FREQ_VCO_MAX
        DEFAULT_DIVIDER = FREQ_VCO_MAX


        def __init__(self, si, idx):
            self._si = si
            self._idx = idx
            self._name = 'N{}'.format(self._si.PLLs[self._idx])
            self._source = None
            self._divider = int(self.DEFAULT_FVCO / self._si.xtal.freq)
            self.set_input_source(xtal_as_source = True)
            self.reset()


        @property
        def freq(self):
            freq = self.source.freq * self.divider  # using "*", not "/" for PLL
            assert self.FREQ_VCO_MIN <= freq <= self.FREQ_VCO_MAX, 'Fvco must be between 600~900MHz.'
            return freq


        def set_frequency(self, freq):
            d = freq / self.source.freq
            a = int(d)
            b = (d - a) * self._si.POW_2_DENOMINATOR_BITS
            c = self._si.POW_2_DENOMINATOR_BITS
            self._set_divider(a, b, c)
            self._frequency = freq
            self._si.restore_clocks_freqs()  # adjust multisynches for each clocks.
            return True


        def reset_plls(self):
            self._si._write_register_by_name('PLL_Reset', 0xA0)
            self._si._read_register_by_name('PLL_Reset')  # Synch. These are self clearing bits.


        def reset(self):
            element_name = 'PLL{}_RST'.format(self._si.PLLs[self._idx])
            self._si._write_element_by_name(element_name, 1)
            self._si._read_element_by_name(element_name)  # Synch. This is a self clearing bit.


        def set_input_source(self, xtal_as_source = True):
            """
            If spread spectrum is not enabled, either of the two PLLs may be used as the source for any outputs of the
            Si5351A.
            If both XTAL and CLKIN input options are used simultaneously (Si5351C only), then one PLL must be
            reserved for use with CLKIN and one for use with the XTAL.
            Note: PLLA must be used for any spread spectrum-enabled outputs. PLLB must be used for any VCXO outputs.

            If a PLL needs to be synchronized to a CMOS clock, PLLx_SRC must be 1.
            The input frequency range of the PLL is 10 to 40 MHz. If CLKIN is > 40 MHz,
            the CLKIN input divider must be used to bring the PLL input within the 10–40 MHz range.
            See CLKIN_DIV[1:0], register 15, bits [7:6].
            """
            self._source = self._si.xtal if xtal_as_source else self._si.clkin
            self._frequency = math.floor(self.source.freq * self.divider)

            element_name = 'PLL{}_SRC'.format(self._si.PLLs[self._idx])
            self._si._write_element_by_name(element_name, 0 if xtal_as_source else 1)
            if not xtal_as_source:
                self._si.clkin._set_divider()


        def _set_integer_mode(self, value = True):
            """
               If a + b/c is an even integer, integer mode may be enabled for PLLA or PLLB by setting parameter FBA_INT or
               FBB_INT respectively. In most cases setting this bit will improve jitter when using even integer divide values.
               Whenever spread spectrum is enabled, FBA_INT must be set to 0.
               """
            self._si._write_element_by_name('FB{}_INT'.format(self._si.PLLs[self._idx]), 1 if value else 0)


        def _validate_abc(self, a, b, c):
            a = int(a)
            b = int(b)
            c = int(c)
            _is_even_integer = self._is_abc_even_integer(a, b, c)

            assert self.DIVIDER_MIN + 1 / (self._si.POW_2_DENOMINATOR_BITS - 1) <= (a + b / c) <= self.DIVIDER_MAX, \
                'Must {} + 1 / ((2 ** {}) - 1) <= (a + b / c) <= {}'.format(self.DIVIDER_MIN,
                                                                            self._si.DENOMINATOR_BITS,
                                                                            self.DIVIDER_MAX)

            return a, b, c, _is_even_integer


    class _Clock(_MultisynthBase):

        DIVIDER_MIN = 1
        DIVIDER_MAX = 128


        def __init__(self, si, idx,
                     enable = False,
                     source = 'MultiSynth',
                     strength_mA = 8,
                     disable_state = 'LOW'):

            super().__init__(si, idx)

            self.enable(enable)
            self.set_input_source(source)
            self._set_strength(strength_mA)
            self._set_disable_state(disable_state)
            self.set_frequency(self._si.FREQ_MCLK)


        def set_input_source(self, source = 'MultiSynth'):
            """
            Generally, Multisynth x should be output on CLKx, however XO, CLKIN, or a divided version of either (see section
            4.2.2 on R dividers) may also be output on each of the CLKx pins. Additionally, MS0 (or a divided version of MS0)
            may be output on CLK0-CLK3, and MS4 (or a divided version of MS4) may be output on CLK4-CLK7. See
            CLKx_SRC description for details.
            """
            valids = self._si.CLOCK_SOURCEs.keys()
            assert source in valids, 'valid sources: {}'.format(valids)

            self._source = {'XTAL'            : self._si.xtal,
                            'CLKIN'           : self._si.clkin,
                            'Group_MultiSynth': self._si.multisynthes[self._idx // 4],
                            'MultiSynth'      : self._si.multisynthes[self._idx]}[source]

            self._frequency = math.floor(self.source.freq / self.divider)
            self._si._write_element_by_name('CLK{}_SRC'.format(self._idx), self._si.CLOCK_SOURCEs[source])


        def set_frequency(self, freq):
            for d in list(self._si.R_DIVIDERs.keys()):
                if math.floor(self.source.freq / d) == math.floor(freq):
                    self._set_divider(d)  # do it within
                    self._frequency = freq
                    return True
                else:
                    if self.source.set_frequency(freq * d) is True:
                        self._set_divider(d)  # source can provide the desired freq, adjust R divider again.
                        self._frequency = freq
                        return True


        @property
        def enabled(self):
            return self._si.map.elements['CLK{}_OEB'.format(self._idx)]['element'].value == 0


        def enable(self, value = True):
            self._si._action = 'enable_output_clock: {}'.format(value)
            self._si._write_element_by_name('CLK{}_OEB'.format(self._idx), 0 if value else 1)
            self.power_down(not value)


        @property
        def power_downed(self):
            return self._si.map.elements['CLK{}_PDN'.format(self._idx)]['element'].value == 1


        def power_down(self, value = True):
            self._si._write_element_by_name('CLK{}_PDN'.format(self._idx), 1 if value else 0)


        def _set_strength(self, mA = 8):
            valids = self._si.OUTPUT_STRENGTHs.keys()
            assert mA in valids, 'valid mA: {}'.format(valids)
            self._si._write_element_by_name('CLK{}_IDRV'.format(self._idx), self._si.OUTPUT_STRENGTHs[mA])


        def _set_invert(self, value = True):
            self._si._write_element_by_name('CLK{}_INV'.format(self._idx), 1 if value else 0)


        def _mask_oeb(self, value = True):
            self._si._action = 'enable_output_clock_oeb_mask: {}'.format(value)
            self._si._write_element_by_name('OEB_MASK{}'.format(self._idx), 1 if value else 0)


        def _set_disable_state(self, state = 'LOW'):
            valids = self._si.DISABLE_STATEs.keys()
            assert state in valids, 'valid states: {}'.format(valids)
            self._si._write_element_by_name('CLK{}_DIS_STATE'.format(self._idx), self._si.DISABLE_STATEs[state])


        def _set_divider(self, divider = 1):
            """
            The R dividers can be used to generate frequencies below about 500 kHz. Each individual output R divider can be
            set to 1, 2, 4, 8,....128 by writing the proper setting for Rx_DIV. Set this parameter to generate frequencies down to
            8kHz
            """
            valids = self._si.R_DIVIDERs.keys()
            assert divider in valids, 'valid divider: {}'.format(valids)

            self._divider = divider
            self._si._write_element_by_name('R{}_DIV'.format(self._idx), self._si.R_DIVIDERs[divider])


        def _enable_phase_offset(self, offset_seconds):
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
            if isinstance(self.source, self._si.Multisynth):
                freq_vco = self.source.source.freq  # PLL
                self._si.multisynthes[self._idx]._set_integer_mode(False)
            else:
                freq_vco = self.source.freq  # XTAL, CLKIN

            offset = round(offset_seconds * 4 * freq_vco)
            self._set_initial_phase_offset(offset)


        def _set_initial_phase_offset(self, value = 0):
            """
            CLKx_PHOFF[6:0] is an unsigned integer with one LSB equivalent to a time delay of
            Tvco/4, where Tvco is the period of the VCO/PLL associated with this output.
            """
            assert self._idx in range(6)
            self._si._write_element_by_name('CLK{}_PHOFF'.format(self._idx), value & 0x3F)


    class _SpreadSpectrum:

        def __init__(self, si):
            self._si = si
            self.enable(False)


        def enable(self, value = True):
            """
            spread spectrum is only supported by PLLA, and the VCXO functionality is only supported by PLLB.
            When using the VCXO function, set the MSNB divide ratio a + b/c such that c = 10**6. This must
            be taken into consideration when configuring a frequency plan.

            Whenever spread spectrum is enabled, FBA_INT must be set to 0.

              The Spread Spectrum Enable control pin is available on the Si5351A and B devices. Spread spectrum enable
            functionality is a logical OR of the SSEN pin and SSC_EN register bit, so for the SSEN pin to work properly, the
            SSC_EN register bit must be set to 0.
            """
            if value:
                self._si.plls[self._si.PLLs.index('A')]._set_integer_mode(False)
            self._si._write_element_by_name('SSC_EN', 1 if value else 0)


        def enable_ssen_pin(self, value = True):
            '''
            The Spread Spectrum Enable control pin is available on the Si5351A and B devices. Spread spectrum enable
            functionality is a logical OR of the SSEN pin and SSC_EN register bit, so for the SSEN pin to work properly, the
            SSC_EN register bit must be set to 0.
            '''
            if value:
                self.enable(True)
                self._si._write_element_by_name('SSC_EN', 0)


        def set_down_spread(self, ssc_amp = 0.01):
            """
            For down spread, four spread spectrum parameters need to be written: SSUDP[11:0], SSDN_P1[11:0],
            SSDN_P2[14:0], and SSDN_P3[14:0].
            """
            pll = self._si.plls[self._si.PLLs.index('A')]
            freq_pfd = pll.source.freq

            ssudp = math.floor(freq_pfd / (4 * 31500))

            ssdn = 64 * pll.divider * ssc_amp / ((1 + ssc_amp) * ssudp)
            ssdn_p1 = math.floor(ssdn)
            ssdn_p2 = 32767 * (ssdn - ssdn_p1)
            ssdn_p3 = 32767

            ssup_p1 = 0,
            ssup_p2 = 0
            ssup_p3 = 1

            self._set_parameters('UDP', ssudp)
            self._set_parameters('UP', ssup_p1, ssup_p2, ssup_p3)
            self._set_parameters('DN', ssdn_p1, ssdn_p2, ssdn_p3)

            return ssudp, (ssup_p1, ssup_p2, ssup_p3), (ssdn_p1, ssdn_p2, ssdn_p3)


        def set_center_spread(self, ssc_amp = 0.01):
            """
            For center spread, seven spread spectrum parameters need to be written: SSUDP[11:0], SSDN_P1[11:0],
            SSDN_P2[14:0], SSDN_P3[14:0], SSUP_P1[11:0], SSUP_P2[14:0], and SSUP_P3[14:0].
            """
            pll = self._si.plls[self._si.PLLs.index('A')]
            freq_pfd = pll.source.freq

            ssudp = math.floor(freq_pfd / (4 * 31500))

            ssup = 128 * pll.divider * ssc_amp / ((1 - ssc_amp) * ssudp)
            ssup_p1 = math.floor(ssup)
            ssup_p2 = 32767 * (ssup - ssup_p1)
            ssup_p3 = 32767

            ssdn = 128 * pll.divider * ssc_amp / ((1 + ssc_amp) * ssudp)
            ssdn_p1 = math.floor(ssdn)
            ssdn_p2 = 32767 * (ssdn - ssdn_p1)
            ssdn_p3 = 32767

            self._set_parameters('UDP', ssudp)
            self._set_parameters('UP', ssup_p1, ssup_p2, ssup_p3)
            self._set_parameters('DN', ssdn_p1, ssdn_p2, ssdn_p3)

            return ssudp, (ssup_p1, ssup_p2, ssup_p3), (ssdn_p1, ssdn_p2, ssdn_p3)


        def _set_parameters(self, name, p1, p2 = None, p3 = None):
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
                 n_channels = N_OUTPUT_CLOCKS,
                 freq_xtal = FREQ_MCLK, freq_clkin = FREQ_MCLK, freq_vcxo = FREQ_MCLK,
                 commands = None):

        registers_map = _get_registers_map() if registers_map is None else registers_map

        super().__init__(n_channels = n_channels, freq_mclk = freq_xtal,
                         registers_map = registers_map, registers_values = registers_values,
                         commands = commands)

        self._i2c = I2C(i2c, i2c_address)
        self._i2c_address = i2c_address
        self._pin_oeb = pin_oeb
        self._pin_ssen = pin_ssen

        # internal components
        self.interrupts = self._Interrupts(self)
        self.xtal = self._Xtal(self, freq_xtal)
        self.clkin = self._CLKIN(self, freq_clkin)
        self.vcxo = self._VCXO(self, freq_vcxo)
        self.plls = [self._PLL(self, i) for i in range(self.N_PLLS)]
        self.multisynthes = [self._Multisynth(self, i) for i in range(self.N_OUTPUT_CLOCKS)]
        self.clocks = [self._Clock(self, i) for i in range(self.N_OUTPUT_CLOCKS)]
        self.spread_spectrum = self._SpreadSpectrum(self)

        self.init()


    def init(self):

        # step 4: define inputs and features
        #     input mode
        #         mode enable/disable
        # self.enable(False)

        #         frequency 25/27 MHz
        #         internal load 0/6/8/10 pF
        # self.xtal.set_crystal_internal_load_capacitance(pF = 10)

        #     Feature
        #         Spread Spectrum Clock Config
        #             enable True/False
        # self.spread_spectrum.enable(False)

        #             direction down/center
        #             amplitude 0.1%
        # step 5: define output frequencies
        #     Out0
        #         mode enabled/disabled/unused

        self.clocks[0].enable()
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
        self._enable_all_outputs(value)


    def enable(self, value = True):
        self._action = 'enable {}'.format(value)
        self._power_down_all_outputs(not value)
        self.enable_output(value)


    def restore_clocks_freqs(self):
        for clk in self.clocks:
            clk.restore_frequency()


    def find_integer_dividers(self, freq_desired, even_only = True, torance_hz = 1, freq_ref = FREQ_MCLK):

        # hierachy structure
        xtal = self._Xtal(self, freq_ref)
        pll = self._PLL(self, 0)
        multisynth = self._Multisynth(self, 0)
        clock = self._Clock(self, 0)

        pll._source = xtal
        multisynth._source = pll
        clock._source = multisynth

        # possible dividers
        divider_plls = range(pll.DIVIDER_MIN, pll.DIVIDER_MAX + 1)
        divider_multisynthes = range(multisynth.DIVIDER_MIN, multisynth.DIVIDER_MAX + 1)
        divider_rs = list(self.R_DIVIDERs.keys())

        results = []

        for dp in divider_plls:
            for dm in divider_multisynthes:
                for dr in divider_rs:
                    try:
                        if even_only:
                            assert dp % 2 == 0 and dm % 2 == 0

                        pll._divider = dp
                        multisynth._divider = dm
                        clock._divider = dr

                        freq_clock = clock.freq
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
    def status(self):
        return self._read_register_by_name('Device_Status')


    # =================================================================

    def _enable_all_outputs(self, value = True):
        self._write_register_by_name('Output_Enable_Control', 0x00 if value else 0xFF)


    def _power_down_all_outputs(self, value = True):
        for i in range(self.N_OUTPUT_CLOCKS):
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



class Si535x_mini:
    I2C_ADDRESS = 0x60
    N_REGISTERS = 188
    OUTPUT_ENABLE_CONTROL_ADDRESS = 3


    def __init__(self, i2c, i2c_address = I2C_ADDRESS, registers_values = None):
        self._i2c = I2C(i2c, i2c_address)
        self._i2c_address = i2c_address

        self.enable(False)

        if registers_values is not None:
            self.write_all_registers(registers_values)

        self.enable(True)


    def enable(self, value = True):
        self.write_register(self.OUTPUT_ENABLE_CONTROL_ADDRESS, 0x00 if value else 0xFF)


    def read_register(self, address):
        return self._i2c.read_byte(address)


    def read_all_registers(self):
        addressed_values = []
        for address in range(self.N_REGISTERS):
            try:
                value = self.read_register(address)
                addressed_values.append((address, value))
            except:
                pass
        return addressed_values


    def write_register(self, address, value):
        return self._i2c.write_byte(address, value)


    def write_all_registers(self, addressed_values):
        for (address, value) in addressed_values:
            try:
                self.write_register(address, value)
            except:
                pass
