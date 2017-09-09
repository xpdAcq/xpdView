"""module to start pure mpl-backend viewer"""
import matplotlib.pyplot as plt
import numpy as np
from .cross_2d import StackViewer, CrossSection
from .waterfall import Waterfall

# init
viewer_fig = plt.figure()  # let mpl decide backend
cross_section = CrossSection(viewer_fig)
stack_viewer = StackViewer(cross_section)

waterfall_fig = plt.figure()  # let mpl decide backend
waterfall = Waterfall(waterfall_fig, waterfall_fig.canvas)

# def data list to test
img_data_list = []
key_list = []
int_data_list = []
for i in range(5):
    key_list.append(str(i))
    img_data_list.append(np.random.rand(50, 50))
    int_data_list.append((np.linspace(0, 200, 200),
                          np.random.rand(200,1)))

plt.show()
