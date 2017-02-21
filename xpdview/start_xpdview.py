import os
import sys
import numpy as np
try:
    from PyQt5 import QtWidgets
    from xpdview.viewer_qt5 import XpdView
    app = QtWidgets.QApplication(sys.argv)
except:
    from PyQt4 import QtGui
    from xpdview.viewer_qt4 import XpdView
    app = QtGui.QApplication(sys.argv) 
viewer = XpdView()
viewer.show()

# def data list to test
img_data_list = []
key_list = []
int_data_list = []
for i in range(5):
    key_list.append(str(i))
    img_data_list.append(np.random.rand(50, 50))
    int_data_list.append((np.linspace(0, 200, 200),
                          np.random.rand(200,1)))
