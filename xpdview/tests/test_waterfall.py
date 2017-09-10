import numpy as np
import matplotlib.pyplot as plt
from xpdview.waterfall import Waterfall

fig = plt.figure('test_title')
unit = ('x unit', 'y unit')
int_data_list = []
key_list = []

x = np.linspace(0, 4*np.pi, 200)
for i in range(5):
    key_list.append(str(i))
    int_data_list.append((x, np.sin(x)))

p1 = Waterfall()
p2 = Waterfall(fig, key_list=key_list, int_data_list=int_data_list,
               unit=unit)

plt.show()
