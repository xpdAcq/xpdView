"""module to start pure mpl-backend viewer"""
import matplotlib.pyplot as plt
import numpy as np
from xpdview.cross_2d import StackViewer, CrossSection
from xpdview.waterfall import Waterfall

# def data list to test
img_data_list = []
key_list = []
int_data_list = []
x = np.linspace(0, 2*np.pi, 200)
for i in range(5):
    key_list.append(str(i))
    img_data_list.append(np.random.rand(50, 50))
    int_data_list.append((x, np.sin(x)))

# init
viewer_fig = plt.figure('test_viewer')  # let mpl decide backend
cross_section = CrossSection(viewer_fig)
stack_viewer = StackViewer(cross_section, img_data_list=img_data_list,
                           key_list=key_list)
waterfall_fig = plt.figure('test_waterfall')  # let mpl decide backend
waterfall = Waterfall(fig=waterfall_fig, key_list=key_list,
                      int_data_list=int_data_list,
                      unit=('x_unit', 'y_unit'))
plt.show()
