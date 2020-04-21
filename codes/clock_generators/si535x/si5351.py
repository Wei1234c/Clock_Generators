try:
    from ..si535x.si535x import *
except Exception as e:
    from si535x import *



class Si5351A_B_GT(Si535x):

    OUTPUT_CLOCKS_IN_USE = (0, 1, 2)