try:
    from ..si535x.si535x import *
except Exception as e:
    from si535x import *



class Si5351(Si535x):
    pass



class Si5351_mini(Si535x_mini):
    pass
