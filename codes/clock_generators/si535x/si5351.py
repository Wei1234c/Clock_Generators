
try:
    from ..si535x.si535x import *
except Exception as e:
    print(e)
    from si535x import *



class Si5351(Si535x):
    DEBUG_MODE = False
    REGISTERS_COUNT = 2
    FREQ_MCLK = int(25e6)