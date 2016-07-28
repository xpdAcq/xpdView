"""
This file will contain the code to create the XPD view GUI
"""

from xray_vision.qt_widgets import CrossSectionMainWindow
from PyQt4 import QtGui, QtCore
import os
import sys
import numpy as np
from Tif_File_Finder import TifFileFinder
from plot_analysis import reducedRepPlot


def data_gen(length):
    x, y = [_ * 2 * np.pi / 200 for _ in np.ogrid[-1000:1000, -1000:1000]]
    rep = int(np.sqrt(length))
    data = []
    for idx in range(length):
        kx = idx // rep + 1
        ky = idx % rep
        data.append(np.sin(kx * x) * np.cos(ky * y) + 1.05)
    return data


class Display(QtGui.QMainWindow):

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('XPD View')
        self.analysis_type = None
        self.file_path = None
        self.analysis_list = ["min", "max", "mean", "Standard Deviation", "Total Intensity"]

        self.key_list = ['Home']
        self.data_list = data_gen(1)
        self.Tif = TifFileFinder()

        self._main_window = CrossSectionMainWindow(data_list=self.data_list,
                                                   key_list=self.key_list,
                                                   cmap='RdBu')

        self._main_window.setFocus()
        self.setCentralWidget(self._main_window)

        # set path option
        setpath = QtGui.QAction("&Set Directory", self)
        setpath.setShortcut("Ctrl+O")
        setpath.setStatusTip("Set image directory")
        setpath.triggered.connect(self.set_path)

        # sets up refresh button
        refresh = QtGui.QAction("&Refresh Files", self)
        refresh.triggered.connect(self.refresh)

        # set analysis type options
        # select_mean = QtGui.QAction("&mean", self)
        # select_mean.triggered.connect(self.set_type_mean)
        #
        # select_std_dev = QtGui.QAction("&standard deviation", self)
        # select_std_dev.triggered.connect(self.set_type_stddev)
        #
        # select_min = QtGui.QAction("&min", self)
        # select_min.triggered.connect(self.set_type_min)
        #
        # select_max = QtGui.QAction("&max", self)
        # select_max.triggered.connect(self.set_type_max)
        #
        # select_total_intensity = QtGui.QAction("&total intensity", self)
        # select_total_intensity.triggered.connect(self.set_type_total)

        plt_action = QtGui.QAction("&Plot", self)
        plt_action.setShortcut("Ctrl+P")
        plt_action.triggered.connect(self.set_graph_settings)

        self.statusBar()

        # This sets up all of the menu widgets that are used in the GUI
        mainmenu = self.menuBar()
        filemenu = mainmenu.addMenu("&File")
        graph_menu = mainmenu.addMenu('&Reduced Represenation')
<<<<<<< HEAD
        analysis_submenu = QtGui.QMenu("analysis settings", graph_menu)
=======
        #graph_menu.triggered.connect(self.set_graph_settings)
        # analysis_submenu = QtGui.QMenu("analysis settings", graph_menu)
>>>>>>> 85d140c407a48ea9d46c7490b1882c37cd43d8ec
        filemenu.addAction(setpath)
        filemenu.addAction(refresh)
        # analysis_submenu.addAction(select_max)
        # analysis_submenu.addAction(select_min)
        # analysis_submenu.addAction(select_mean)
        # analysis_submenu.addAction(select_std_dev)
        # analysis_submenu.addAction(select_total_intensity)
        #graph_menu.addMenu(analysis_submenu)
        graph_menu.addAction(plt_action)

        self._main_window._messenger._ctrl_widget._spin_img.valueChanged.connect(self.thingy)
        self.show()

    def set_path(self):
        popup = QtGui.QFileDialog()
        self.file_path = str(popup.getExistingDirectory())
        self.Tif._directory_name = self.file_path
        self.Tif.get_file_list()
        self.update_data(self.Tif.pic_list, self.Tif.file_list)

    def set_graph_settings(self):
        menu = QtGui.QDialog(self)
        menu.setWindowTitle("Reduced Representation Settings")
        menu.setWindowModality(QtCore.Qt.ApplicationModal)
        #menu.setGeometry(300, 300, 800, 300)
        vbox = QtGui.QVBoxLayout()
        hbox_lim_labels = QtGui.QHBoxLayout()
        hbox_lim_widgets = QtGui.QHBoxLayout()

        # creating qt widgets
        analysis_selector = QtGui.QComboBox(menu)
        analysis_selector.addItems(self.analysis_list)

        print(self._main_window._messenger._fig.axes[0].get_xlim())
        print(self._main_window._messenger._fig.axes[0].get_ylim())

        a_selector_label = QtGui.QLabel()
        x_min_label = QtGui.QLabel()
        x_max_label = QtGui.QLabel()
        y_min_label = QtGui.QLabel()
        y_max_label = QtGui.QLabel()

        a_selector_label.setText("Analysis Type")
        x_min_label.setText("x min")
        x_max_label.setText("x max")
        y_min_label.setText("y min")
        y_max_label.setText("y max")

        x_min, x_max = self._main_window._messenger._fig.axes[0].get_xlim()
        x_lim_min = QtGui.QSpinBox()
        x_lim_min.setMinimum(0)
        x_lim_min.setMaximum(2048)
        x_lim_min.setValue(int(x_min))

        x_lim_max = QtGui.QSpinBox()
        x_lim_max.setMinimum(0)
        x_lim_max.setMaximum(2048)
        x_lim_max.setValue(int(x_max))

        y_min, y_max = self._main_window._messenger._fig.axes[0].get_ylim()
        y_lim_min = QtGui.QSpinBox()
        y_lim_min.setMinimum(0)
        y_lim_min.setMaximum(10000)
        y_lim_min.setValue(int(y_min))

        y_lim_max = QtGui.QSpinBox()
        y_lim_max.setMinimum(0)
        y_lim_max.setMaximum(10000)
        y_lim_max.setValue(int(y_max))

        plt_btn = QtGui.QPushButton()
        plt_btn.setText("Plot")
        plt_btn.clicked.connect(menu.close)
        plt_btn.clicked.connect(lambda: self.set_analysis_type(analysis_selector.currentIndex()))
        plt_btn.clicked.connect(lambda: self.plot_analysis(x_lim_min.value(), x_lim_max.value(),
                                                           y_lim_min.value(), y_lim_max.value()))

        #defining layout
        vbox.addStretch()
        vbox.addWidget(a_selector_label)
        vbox.addStretch()
        vbox.addWidget(analysis_selector)
        vbox.addStretch()
        #defining label horizontal layout
        hbox_lim_labels.addStretch()
        hbox_lim_labels.addWidget(x_min_label)
        hbox_lim_labels.addStretch()
        hbox_lim_labels.addWidget(x_max_label)
        hbox_lim_labels.addStretch()
        hbox_lim_labels.addWidget(y_min_label)
        hbox_lim_labels.addStretch()
        hbox_lim_labels.addWidget(y_max_label)
        hbox_lim_labels.setAlignment(QtCore.Qt.AlignLeft)

        vbox.addLayout(hbox_lim_labels)
        vbox.addStretch()

        #defining widget horizontal layout
        hbox_lim_widgets.addStretch()
        hbox_lim_widgets.addWidget(x_lim_min)
        hbox_lim_widgets.addStretch()
        hbox_lim_widgets.addWidget(x_lim_max)
        hbox_lim_widgets.addStretch()
        hbox_lim_widgets.addWidget(y_lim_min)
        hbox_lim_widgets.addStretch()
        hbox_lim_widgets.addWidget(y_lim_max)
        hbox_lim_widgets.setAlignment(QtCore.Qt.AlignLeft)

        vbox.addLayout(hbox_lim_widgets)
        vbox.addStretch()
        vbox.addWidget(plt_btn)

        menu.setLayout(vbox)
        menu.show()
        menu.exec_()


    def set_analysis_type(self, i):
        self.analysis_type = self.analysis_list[i]

    def plot_analysis(self, x_min, x_max, y_min, y_max):
        try:
            rpp = reducedRepPlot(self.data_list, x_min, x_max, y_min, y_max, self.analysis_type)
            rpp.plot()
        except NotADirectoryError:
            print("exception excepted")
            err_msg_file = QtGui.QMessageBox()
            err_msg_file.setIcon(QtGui.QMessageBox.Critical)
            err_msg_file.setWindowTitle("Error")
            err_msg_file.setText("You did not specify a file path.")
            err_msg_file.setInformativeText("click open to set the file path")
            err_msg_file.setStandardButtons(QtGui.QMessageBox.Open)
            err_msg_file.buttonClicked.connect(self.set_path)
            err_msg_file.exec_()
        except AssertionError:
            err_msg_analysis = QtGui.QMessageBox()
            err_msg_analysis.setIcon(QtGui.QMessageBox.Critical)
            err_msg_analysis.setWindowTitle("Error")
            err_msg_analysis.setText("The limits are incorrect")
            err_msg_analysis.setInformativeText("x_min must be less than x_max \n y_min must be greater than y_max")
            err_msg_analysis.setStandardButtons(QtGui.QMessageBox.Close)
            # err_msg_analysis.buttonClicked.connect(self.set_path)
            err_msg_analysis.exec_()


    def refresh(self):
        new_file_names, new_data = self.Tif.get_new_files()
        if len(new_file_names) == 0:
            print("No new .tif files found")
        else:
            self.update_data(new_data, new_file_names)

    def update_data(self, data_list, file_list):
        # This method updates the data in the image displayer taking in some new data list and some other
        # list that is normally the list of File names
        old_length = len(self.key_list)
        for file in file_list:
            self.key_list.append(file)
        for data in data_list:
            self.data_list.append(data)
        for i in range(old_length, len(self.key_list)):
            self._main_window._messenger._view._data_dict[self.key_list[i]] = self.data_list[i]
        self._main_window._messenger._ctrl_widget._slider_img.setMaximum(len(self.key_list) - 1)
        self._main_window._messenger._ctrl_widget._spin_img.setMaximum(len(self.key_list) - 1)

    def thingy(self, val):
        print(val)


def main():
    app = QtGui.QApplication(sys.argv)
    viewer = Display()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()