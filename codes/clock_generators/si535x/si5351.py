try:
    from ..si535x.si535x import *
except Exception as e:
    from si535x import *



class Si5351(Si535x):

    OUTPUT_CLOCKS_IN_USE = (0, 1, 2)
