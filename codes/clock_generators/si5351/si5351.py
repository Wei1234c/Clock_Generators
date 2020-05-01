from .si5351a import Si5351A_B_GT, _section_value, _value_key, OrderedDict, math



class Si5351(Si5351A_B_GT):
    N_OUTPUT_CLOCKS = 8
    OUTPUT_CLOCKS_IN_USE = (0, 1, 2)

    HAS_VCXO = False


    class _CLKIN(Si5351A_B_GT._CLK):
        CLKIN_DIVIDERS = {1: 0x00, 2: 0x01, 4: 0x20, 8: 0x03}


        def _set_divider(self, _ = None):
            for d in sorted(self.CLKIN_DIVIDERS.keys()):
                if self._freq / d <= 40e6:
                    break

            assert self._si._PLL.FREQ_INPUT_MIN <= self._freq / d <= self._si._PLL.FREQ_INPUT_MAX, 'The input frequency range of the PLLis should be between {:0.2e} to {:0.2e} Hz'.format(
                self._si._PLL.FREQ_INPUT_MIN, self._si._PLL.FREQ_INPUT_MAX)

            self._divider = d
            self._si._write_element_by_name('CLKIN_DIV', self.CLKIN_DIVIDERS[d])


        def enable_fanout(self, value = True):
            self._si._action = 'enable_fanout {}'.format(value)
            self._si._write_element_by_name('CLKIN_FANOUT_EN', 1 if value else 0)


    class _VCXO(Si5351A_B_GT._CLK):

        DENOMINATOR_MAX = 10 ** 6


        def __init__(self, si):
            super().__init__(si, None)


        @property
        def pll(self):
            return self._si.plls['B']


        @property
        def freq(self):
            return self.pll.freq


        def set_input_source(self):

            # The VCXO functionality is only supported by PLLB. When using the VCXO function,
            # set the MSNB divide ratio a + b/c such that c = 10^6. This must be taken into consideration
            # when configuring a frequency plan.

            self._source = self.pll
            self.pll.denominator_max = self.DENOMINATOR_MAX


        def enable_fanout(self, value = True):
            pass


        def set_pull_range(self, apr_ppm = 30):
            self._set_parameters(apr_ppm)


        def _set_parameters(self, apr_ppm):

            # The Si5351B combines free-running clock generation and a VCXO in a single package. The VCXO architecture of
            # the Si5350B eliminates the need for an external pullable crystal. The “pulling” is done at PLLB. Only a standard,
            # low cost, fixed-frequency (25 or 27 MHz) AT-cut crystal is required and is used as the reference source for both
            # PLLA and PLLB.
            # PLLB must be used as the source for any VCXO output clock. Feedback B Multisynth divider ratio must be set
            # such that the denominator, c, in the fractional divider a + b/c is fixed to 10^6. Set VCXO_Param register value
            # according to the equation below. Note that 1.03 is a margining factor to ensure the full desired pull range is
            # achieved. For a desired pull-range of +/– 30 ppm, the value APR in the equation below is 30, for +/– 60 ppm APR
            # is 60, and so on.
            #
            # VCXO_Param[21:0] =  1.03 * (128a +  b/10**6) * APR

            pll_divider = self.pll.divider
            a = int(pll_divider)
            b = self.DENOMINATOR_MAX * (pll_divider - a)
            c = self.DENOMINATOR_MAX
            vcxo_p = math.floor(1.03 * (128 * a + b / c) * apr_ppm)

            bits_ranges = ((21, 16), (15, 8), (7, 0))

            for bits_range in bits_ranges:
                idx_msb, idx_lsb = bits_range
                element_name = 'VCXO_Param_{}_{}'.format(idx_msb, idx_lsb)
                self._si._write_element_by_name(element_name, _section_value(vcxo_p, idx_msb, idx_lsb))

            return vcxo_p


        def _set_divider(self, _ = None):
            self._divider = 1


    class _SpreadSpectrum:
        MODES = {'down': 0, 'center': 1}
        MODES_value_key = _value_key(MODES)

        DENOMINATOR_BITS = 15
        DENOMINATOR_MAX = 2 ** DENOMINATOR_BITS - 1


        def __init__(self, si):
            self._si = si
            self.enable(False)


        @property
        def status(self):
            return OrderedDict({'type'       : self.__class__.__name__,
                                'source_freq': self.pll.freq,
                                'mode'       : self.mode,
                                'enabled'    : self.enabled})


        @property
        def pll(self):
            return self._si.plls['A']


        @property
        def freq(self):
            return self.pll.freq


        @property
        def mode(self):
            return self.MODES_value_key[self._si.map.value_of_element('SSC_MODE')]


        @property
        def source(self):
            return self.pll


        @property
        def enabled(self):
            return self._si.map.value_of_element('SSC_EN') == 1


        def enable(self, value = True, mode = 'center', ssc_amp = 0.01):
            self._si._action = 'enable Spread Spectrum {}'.format(value)

            # spread spectrum is only supported by PLLA, and the VCXO functionality is only supported by PLLB.
            # When using the VCXO function, set the MSNB divide ratio a + b/c such that c = 10**6. This must
            # be taken into consideration when configuring a frequency plan.
            # 
            # Whenever spread spectrum is enabled, FBA_INT must be set to 0.
            # 
            #   The Spread Spectrum Enable control pin is available on the Si5351A and B devices. Spread spectrum enable
            # functionality is a logical OR of the SSEN pin and SSC_EN register bit, so for the SSEN pin to work properly, the
            # SSC_EN register bit must be set to 0.

            valids = self.MODES.keys()
            assert mode in valids, 'valid mode: {}'.format(valids)

            if value:
                self.pll._set_integer_mode(False)

                if mode.lower() == 'center':
                    self._set_center_spread(ssc_amp)
                else:
                    self._set_down_spread(ssc_amp)

            self._si._write_element_by_name('SSC_EN', 0)  # need to disable between switched modes.
            self._si._write_element_by_name('SSC_EN', 1 if value else 0)

            self.pll.reset()


        def enable_ssen_pin(self, value = True):
            self._si._action = 'enable_ssen_pin {}'.format(value)

            # The Spread Spectrum Enable control pin is available on the Si5351A and B devices. Spread spectrum enable
            # functionality is a logical OR of the SSEN pin and SSC_EN register bit, so for the SSEN pin to work properly, the
            # SSC_EN register bit must be set to 0.

            if value:
                self.enable(True)
                self._si._write_element_by_name('SSC_EN', 0)


        def _set_down_spread(self, ssc_amp):
            self._si._action = 'set_down_spread ssc_amp {}'.format(ssc_amp)

            # For down spread, four spread spectrum parameters need to be written: SSUDP[11:0], SSDN_P1[11:0],
            # SSDN_P2[14:0], and SSDN_P3[14:0].

            freq_pfd = self.pll.source.freq

            ssudp = math.floor(freq_pfd / (4 * 31500))

            ssdn = 64 * self.pll.divider * ssc_amp / ((1 + ssc_amp) * ssudp)
            ssdn_p1 = math.floor(ssdn)
            ssdn_p2 = math.floor(self.DENOMINATOR_MAX * (ssdn - ssdn_p1))
            ssdn_p3 = self.DENOMINATOR_MAX

            ssup_p1 = 0
            ssup_p2 = 0
            ssup_p3 = self.DENOMINATOR_MAX

            self._set_parameters('UDP', ssudp, 0, 1)
            self._set_parameters('UP', ssup_p1, ssup_p2, ssup_p3)
            self._set_parameters('DN', ssdn_p1, ssdn_p2, ssdn_p3)

            self._si._write_element_by_name('SSC_MODE', self.MODES['down'])

            return ssudp, (ssup_p1, ssup_p2, ssup_p3), (ssdn_p1, ssdn_p2, ssdn_p3)


        def _set_center_spread(self, ssc_amp):
            self._si._action = 'set_center_spread ssc_amp {}'.format(ssc_amp)

            # For center spread, seven spread spectrum parameters need to be written: SSUDP[11:0], SSDN_P1[11:0],
            # SSDN_P2[14:0], SSDN_P3[14:0], SSUP_P1[11:0], SSUP_P2[14:0], and SSUP_P3[14:0].

            freq_pfd = self.pll.source.freq

            ssudp = math.floor(freq_pfd / (4 * 31500))

            ssup = 128 * self.pll.divider * ssc_amp / ((1 - ssc_amp) * ssudp)
            ssup_p1 = math.floor(ssup)
            ssup_p2 = math.floor(self.DENOMINATOR_MAX * (ssup - ssup_p1))
            ssup_p3 = self.DENOMINATOR_MAX

            ssdn = 128 * self.pll.divider * ssc_amp / ((1 + ssc_amp) * ssudp)
            ssdn_p1 = math.floor(ssdn)
            ssdn_p2 = math.floor(self.DENOMINATOR_MAX * (ssdn - ssdn_p1))
            ssdn_p3 = self.DENOMINATOR_MAX

            self._set_parameters('UDP', ssudp, 0, 1)
            self._set_parameters('UP', ssup_p1, ssup_p2, ssup_p3)
            self._set_parameters('DN', ssdn_p1, ssdn_p2, ssdn_p3)

            self._si._write_element_by_name('SSC_MODE', self.MODES['center'])

            return ssudp, (ssup_p1, ssup_p2, ssup_p3), (ssdn_p1, ssdn_p2, ssdn_p3)


        def _set_parameters(self, name, p1, p2, p3):

            # Spread spectrum can be enabled on any Multisynth output that uses PLLA as its reference. Valid ranges for spread
            # spectrum include –0.1% to –2.5% down spread and up to ± 1.5% center spread. This spread modulation rate is
            # fixed at approximately 31.5 kHz.
            # The following parameters must be known to properly set up spread spectrum:
            # fPFD(A) input frequency to PLLA in Hz (determined in Sec 2 above and referred to in “3.1.2. CMOS Clock
            # Source”). This is also listed in the ClockBuilder Pro generated register map file as “#PFD(MHz)=...”
            # a + b/c PLLA Multisynth ratio (determined in Sec 2 above).
            # sscAMPSpread amplitude (e.g., for down or center spread amplitude of 1%, sscAmp = 0.01).
            # Use the equations below to set up the desired spread spectrum profile.
            # Note: Make sure MSNA is set up in fractional mode when using the spread spectrum feature. See parameter FBA_INT in register 22.

            valids = ('UP', 'DN', 'UDP')
            assert name in valids, 'valid name: {}'.format(valids)

            params = (p1, p2, p3)

            bits_12 = ((11, 8), (7, 0))
            bits_15 = ((14, 8), (7, 0))
            bits_ranges = {1: bits_12, 2: [], 3: []} if name == 'UDP' else {1: bits_12, 2: bits_15, 3: bits_15}

            for i in range(len(params)):
                param_idx = i + 1
                for bits_range in bits_ranges[param_idx]:
                    idx_msb, idx_lsb = bits_range
                    element_name = 'SSUDP' if name == 'UDP' else 'SS{}_P{}'.format(name, param_idx)
                    element_name = '{}_{}_{}'.format(element_name, idx_msb, idx_lsb)
                    self._si._write_element_by_name(element_name, _section_value(params[i], idx_msb, idx_lsb))

            return p1, p2, p3


    def _build(self):
        super()._build()

        self.clkin = self._CLKIN(self, self._freq_clkin)
        self.spread_spectrum = self._SpreadSpectrum(self)  # PLL_A as source
        if self.HAS_VCXO:
            self.vcxo = self._VCXO(self)  # PLL_B as source, changes PLL_B's denominator(P3) if used.


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


    def find_integer_dividers(self, freq_desired, even_only = True, torance_hz = 1, freq_ref = Si5351A_B_GT.FREQ_REF):

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
