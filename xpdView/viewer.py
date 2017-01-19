##############################################################################
#
# xpdView.xpd_view         SULI and HSRP
#                          (c) 2016 Brookhaven Science Associates,
#                          Brookhaven National Laboratory.
#                          All rights reserved.
#
# File coded by:           Caleb Duff
#                          Joseph Kaming-Thanassi
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
This file will contain the code that makes the XPD view GUI
"""

import sys
import numpy as np
from PyQt4 import QtGui, QtCore
from collections import OrderedDict

import matplotlib
matplotlib.use('Qt4Agg')

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolBar
import matplotlib.pyplot as plt
from xray_vision.messenger.mpl.cross_section_2d import CrossSection2DMessenger

from xpdView.one_dimensional_int import IntegrationPlot
from xpdView.waterfall_2d import Waterfall2D



def data_gen(length):
    """
    This functions generates data for the home page of the Display2 class to create a home page; can also be used
    to create practice data

    Parameters
    ----------
    length : int
        this should be the number of 2D data arrays wanted

    Returns
    -------
    data : list of 2D arrays
        list of 2D arrays that have circular data
    keys : list of strings
        list of strings

    """
    # This will generate circular looking data
    x_length = 100
    y_length = 100
    data = []
    keys = []
    for idx in range(length):
        array_style = np.zeros((x_length, y_length))
        keys.append(str(idx))
        for x in range(x_length):
            for y in range(y_length):
                height = idx + 1
                if x == int(x_length / 2) and y == int(y_length / 2):
                    array_style[x][y] = 0
                else:
                    array_style[x][y] = height / np.sqrt((x - int(x_length / 2)) ** 2 + (y - int(y_length / 2)) ** 2)
        data.append(array_style)
    return data, keys


class Display(QtGui.QMainWindow):
    def __init__(self):
        """
        This class creates the display window that is used by
        users to analyze their data

        Parameters
        ----------
        self

        Returns
        -------
        None
        """
        # This is just setting up some of the beginning variables
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('XPD View')
        # dict to store img arrays: {<name> : array}
        self.img_data_dict = OrderedDict()
        # dict to store int array: {<name> : (x, y)}
        self.int_data_dict = OrderedDict()
        # key and data lists are required by x-ray vision
        # ref:
        ###################################
        # data_list : list
        #    The data stored as a list
        # key_list : list
        #    The order of keys to plot
        #################################
        self.img_data_list, self.img_key_list = data_gen(1)  # dummy val for init CrossSection2D

        self.int_key_list = list(self.int_data_dict.keys())
        self.int_data_list = list(self.int_data_dict.values())

        self.analysis_type = None
        self.setDockNestingEnabled(True)
        self.setAnimated(True)

        # This sets up all we need from the cross section 2D messenger class for use in the code
        self.messenger = CrossSection2DMessenger(data_list=self.img_data_list,
                                                 key_list=self.img_key_list)
        self.display = self.messenger._display
        self.ctrls = self.messenger._ctrl_widget
        self.ctrls.set_image_intensity_behavior('full range')
        self.messenger.sl_update_image(0)
        # link img_data_dict to CrossSection2DMessenger, so that it can be remembered
        self.img_data_dict = self.messenger._view._data_dict

        # These lists will contain references to the pop up plots so that they can be updated
        #self.rpp_list = list()
        #self.three_dim_list = list()
        #self.peak_plots = list()

        #self.func_dict = {np.std.__name__: np.std, np.mean.__name__: np.mean, np.amin.__name__: np.amin,
        #                  np.amax.__name__: np.amax, np.sum.__name__: np.sum}

        # setting up dockable windows
        self.setDockNestingEnabled(True)
        self.setAnimated(False)

        #self.plot_dock = QtGui.QDockWidget("Dockable", self)
        #self.plot_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        #self.plot_dock.setWindowTitle("Reduced Representation")

        self.img_dock = QtGui.QDockWidget("Dockable", self)
        self.img_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.img_dock.setWindowTitle("Image")

        self.integration_dock = QtGui.QDockWidget("Dockable", self)
        self.integration_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.integration_dock.setWindowTitle("Integration")

        self.waterfall_dock = QtGui.QDockWidget("Dockable", self)
        self.waterfall_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.waterfall_dock.setWindowTitle("Waterfall Plot")

        self.is_main_rpp_plotted = False

        # This creates the canvases that all plots within the GUI will be drawn on
        self.fig3 = plt.figure()
        self.canvas3 = FigureCanvas(self.fig3)
        self.fig4 = plt.figure()
        self.canvas4 = FigureCanvas(self.fig4)

        # This creates the widgets so they can be accessed later
        self.name_label = QtGui.QLabel()
        self.img_slider = self.ctrls._slider_img
        self.img_spin = self.ctrls._spin_img
        self.color = self.ctrls._cm_cb
        self.int_style = self.ctrls._cmbbox_intensity_behavior
        self.int_norm = self.ctrls._cmbbox_norm
        self.int_min = self.ctrls._spin_min
        self.int_max = self.ctrls._spin_max

        # These statements add the dock widgets to the GUI
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.img_dock)
        #self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
        #                   self.plot_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.integration_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.waterfall_dock)


        # These methods will set up the menu bars and the tool bars
        self.tools_box = QtGui.QToolBar()
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.tools_box)
        self.set_up_tool_bar()
        self.set_up_menu_bar()

        # These methods begin the process of creating the four tiles to hold the plots
        self.img_dock.setWidget(self.display)
        self.rpp = None
        self.one_dim_plot = None
        self.water = None

    ############ method to update data contents ################
    def update_img_data_dict(self, img_data_dict):
        """method to update img_data_dict

        Parameters
        ----------
        img_data_dict: dict-like object
            a dict stores 2D images.
            Expect format: {<name> : array}
        """
        # update class dict
        self.img_data_dict.update(img_data_dict)
        self.img_key_list = list(self.img_data_dict.keys())
        self.img_data_list = list(self.img_data_dict.values())
        self.update_img_plot_dock()

    def update_img_plot_dock(self):
        """updates the viewer"""

        # configure CrossSectionViewer
        #FIXME use public api to update data
        self.messenger._view._data_dict = self.img_data_dict
        self.messenger._view._key_list = self.img_key_list
        self.img_slider.setMaximum(len(self.img_key_list) - 1)  # python starts from 0
        self.img_spin.setMaximum(len(self.img_key_list) - 1)
        self.messenger.sl_update_image(0)


    def update_int_data_dict(self, int_data_dict):
        """method to update int_data_dict (which is 1D)

        Parameters
        ----------
        int_data_dict : dict-like object
            a dict stores integrated data
            Expected format : {<name> : (x, y)}
        """
        self.int_data_dict.update(int_data_dict)
        self.int_key_list = list(self.int_data_dict.keys())
        self.int_data_list = list(self.int_data_dict.values())

        # update all 1D related plots
        self.update_waterfall_dock()

    def update_waterfall_dock(self):
        """method to update the integrate data related docks"""

        # update waterfall class
        self.waterfall_2d()
        # update 1-D plot class
        self.one_dim_integrate()
        # self.water is configured by self.waterfall2d.....

    def change_frame(self, ind):
        """method to change 1D plot canvas
        Parameters
        ----------
        ind : int
            the value that comes in from the widget

        Returns
        -------
        None

        """
        self.one_dim_plot.give_plot(self.int_key_list[ind])
        self.name_label.setText(self.int_key_list[ind])


    def refresh(self, img_data_dict, int_data_dict):
        """top-level method to refresh data contents and gui"""
        self.update_img_data_dict(img_data_dict)
        self.update_int_data_dict(int_data_dict)
    ################################################################

    ########## method to take care of plotting docks ###############
    def one_dim_integrate(self):
        """
        This creates the bottom left tile and also creates an instance of the IntegrationPlot class for handling
        the plotting of the image

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        FigureCanvas.setSizePolicy(self.canvas3, QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self.canvas3)
        self.one_dim_plot = IntegrationPlot(self.int_data_dict,
                                            self.fig3, self.canvas3)
        toolbar = NavigationToolBar(self.canvas3, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas3)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        self.integration_dock.setWidget(multi)


    def waterfall_2d(self):
        """
        This handles plotting the 2d waterfall
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        # signature as x-ray vision
        self.water = Waterfall2D(self.int_key_list,
                                 self.int_data_dict, fig, canvas)
        self.water.y_offset = .5
        self.water.generate_waterfall()  # draws 1D curves onto plot canvas
        # configure gui layout
        toolbar = self.twod_plot_settings()
        mpl_toolbar = NavigationToolBar(canvas, self)
        layout = QtGui.QVBoxLayout()
        grid = QtGui.QGridLayout()
        grid.addWidget(mpl_toolbar, 0, 0)
        grid.addWidget(toolbar, 1, 0)
        layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        layout.addLayout(grid)
        layout.addWidget(canvas)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        # update object in main gui frame
        self.waterfall_dock.setWidget(multi)
    #####################################################################################

    def click_handling(self, event):
        """
        This method simply tells the display window what to do when someone clicks on the top right tile what to do

        Parameters
        ----------
        event: event
            from mouse click that is used to change the image

        Returns
        -------
        None

        """
        if (event.xdata is not None) and (event.ydata is not None):
            self.img_slider.setValue(int(event.xdata))

    def set_up_menu_bar(self):
        """
        This method creates the menu bar and ties all of the actions associated with the different options to the menu
        bar

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        # set path option
        setpath = QtGui.QAction("&Set Directory", self)
        setpath.setShortcut("Ctrl+O")
        setpath.setStatusTip("Set image directory")
        #setpath.triggered.connect(self.set_path)

        # sets up menu refresh option
        refresh_path = QtGui.QAction('&Refresh', self)
        refresh_path.setShortcut('Ctrl+R')
        #refresh_path.triggered.connect(self.refresh)

        # This sets up the option that makes the popup window for reduced rep plot settings
        plt_action = QtGui.QAction("&Plot", self)
        plt_action.setShortcut("Ctrl+P")
        #plt_action.triggered.connect(self.set_graph_settings)

        # This sets ups the option that makes the peak searching plot
        peak_action = QtGui.QAction("&Find Peaks", self)
        peak_action.setShortcut("Ctrl+F")
        #peak_action.triggered.connect(self.peak_plot)

        # This sets up the options that control the waterfall 2d settings and 3d waterfall creation
        surface_action = QtGui.QAction("&Surface", self)
        #surface_action.triggered.connect(lambda: self.waterfall_3d("surface"))

        twod_action = QtGui.QAction("&Show 2D Waterfall Toolbar", self)
        #twod_action.triggered.connect(self.twod_plot_settings)

        wire_action = QtGui.QAction("&Wire", self)
        #wire_action.triggered.connect(lambda: self.waterfall_3d("wire"))

        # This creates the window redocking option in the code
        reset_windows = QtGui.QAction('&Redock Windows', self)
        reset_windows.triggered.connect(self.reset_window_layout)

        # This sets up all of the menu widgets that are used in the GUI
        mainmenu = self.menuBar()
        #filemenu = mainmenu.addMenu("&File")
        window_menu = mainmenu.addMenu("&Window")
        #graph_menu = mainmenu.addMenu('&Reduced Representation')
        #waterfall_menu = mainmenu.addMenu('&Waterfall Plots')
        #filemenu.addAction(setpath)
        #filemenu.addAction(refresh_path)
        #graph_menu.addAction(plt_action)
        #graph_menu.addAction(peak_action)
        #waterfall_menu.addAction(surface_action)
        #waterfall_menu.addAction(wire_action)
        #waterfall_menu.addAction(twod_action)
        window_menu.addAction(reset_windows)

    def twod_plot_settings(self):
        """
        This creates the pop up window that controls the settings on the 2d waterfall
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        settings_window = QtGui.QDialog(self)
        y_offset_label = QtGui.QLabel()
        y_offset_label.setText("Y Offset")
        y_offset_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        y_offset_slider.setMinimum(0)
        y_offset_slider.setMaximum(20)
        y_offset_slider.valueChanged.connect(self.set_y_offset)
        x_offset_label = QtGui.QLabel()
        x_offset_label.setText("X Offset")
        x_offset_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        x_offset_slider.setMinimum(0)
        x_offset_slider.setMaximum(20)
        x_offset_slider.valueChanged.connect(self.set_x_offset)
        normalize_option_label = QtGui.QLabel()
        normalize_option_label.setText("Normalize data:")
        normalize_option_box = QtGui.QCheckBox()
        # data is normalized by default
        normalize_option_box.setChecked(self.water.is_normalized())
        normalize_option_box.stateChanged.connect(self.set_normalization)
        layout = QtGui.QHBoxLayout()
        for widget in [y_offset_label, y_offset_slider,
                       x_offset_label, x_offset_slider,
                       normalize_option_label, normalize_option_box]:
            layout.addStretch()
            layout.addWidget(widget)

        settings_window.setLayout(layout)
        #settings_window.show()
        #settings_window.exec_()

        return settings_window

    def set_normalization(self, state):
        if state == 2:
            self.water.set_normalized(True)
        else:
            self.water.set_normalized(False)

        self.water.generate_waterfall()

    def set_x_offset(self, value):
        self.water.x_offset = value
        self.water.generate_waterfall()

    def set_y_offset(self, value):
        self.water.y_offset = (value / 10.0)
        self.water.generate_waterfall()

    def set_analysis_type(self, i):
        """
        This method creates the display in the dialog window

        Parameters
        ----------
        self
        i : int
            key chosen in dialog window that sets index

        Returns
        -------
        None

        """
        self.analysis_type = list(self.func_dict.keys())[i]

    def plot_analysis(self, x_min, x_max, y_min, y_max):
        """
        This
        Parameters
        ----------
        x_min : int
            integer that tells which column the analysis software should begin with on the image
        x_max : int
            integer that tells which column the analysis software should end with on the image
        y_min : int
            integer that tells which row the analysis software should begin with on the image
        y_max : int
            integer that tells which row the analysis software should end with on the image

        Returns
        -------
        None

        """
        try:
            self.rpp_list[0].x_start = x_min
            self.rpp_list[0].x_stop = x_max
            self.rpp_list[0].y_start = y_min
            self.rpp_list[0].y_stop = y_max
            self.rpp_list[0].selection = self.analysis_type
            self.rpp_list[0].show()
            self.is_main_rpp_plotted = True
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

    def set_graph_settings(self):
        """
        This function creates the pop up window that allows the user to communicate over what region of the image
        and what statistical parameter they want to observe

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        menu = QtGui.QDialog(self)
        menu.setWindowTitle("Reduced Representation Settings")
        menu.setWindowModality(QtCore.Qt.NonModal)
        vbox = QtGui.QVBoxLayout()
        hbox_lim_labels = QtGui.QHBoxLayout()
        hbox_lim_widgets = QtGui.QHBoxLayout()

        # creating qt widgets
        analysis_selector = QtGui.QComboBox(menu)
        analysis_selector.addItems(list(self.func_dict.keys()))

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

        x_min, x_max = self.messenger._fig.axes[0].get_xlim()
        x_lim_min = QtGui.QSpinBox()
        x_lim_min.setMinimum(0)
        x_lim_min.setMaximum(2048)
        x_lim_min.setValue(int(x_min))

        x_lim_max = QtGui.QSpinBox()
        x_lim_max.setMinimum(0)
        x_lim_max.setMaximum(2048)
        x_lim_max.setValue(int(x_max))

        y_min, y_max = self.messenger._fig.axes[0].get_ylim()
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

        new_plot_btn = QtGui.QPushButton()
        new_plot_btn.setText("Plot in new window")
        new_plot_btn.clicked.connect(menu.close)
        new_plot_btn.clicked.connect(lambda: self.set_analysis_type(analysis_selector.currentIndex()))
        new_plot_btn.clicked.connect(lambda: self.new_r_rep(analysis_selector.currentText(),
                                                            x_lim_min.value(), x_lim_max.value(),
                                                            y_lim_min.value(), y_lim_max.value()))

        # defining layout
        vbox.addStretch()
        vbox.addWidget(a_selector_label)
        vbox.addStretch()
        vbox.addWidget(analysis_selector)
        vbox.addStretch()
        # defining label horizontal layout
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

        # defining widget horizontal layout
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
        vbox.addStretch()
        vbox.addWidget(new_plot_btn)

        menu.setLayout(vbox)
        menu.show()
        menu.exec_()

    def set_up_tool_bar(self):
        """
        This takes all of the widgets that are put into the toolbar and puts them in there

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        # All these commands will add the widgets in their proper order to the tool bar
        self.tools_box.addWidget(self.img_slider)
        self.tools_box.addWidget(self.img_spin)
        self.tools_box.addWidget(self.color)
        min_label = QtGui.QLabel()
        self.tools_box.addWidget(self.int_style)
        self.tools_box.addWidget(self.int_norm)
        min_label.setText('Int Min')
        self.tools_box.addWidget(min_label)
        self.tools_box.addWidget(self.int_min)
        max_label = QtGui.QLabel()
        max_label.setText('Int Max')
        self.tools_box.addWidget(max_label)
        self.tools_box.addWidget(self.int_max)

        # This makes the Label that is used to display the current key name
        self.name_label.setText(self.img_key_list[0])
        self.tools_box.addWidget(self.name_label)

        # This makes sure that the display is updated when the image is changed
        self.img_spin.valueChanged.connect(self.change_frame)

        # This makes the refresh button
        refresh_btn = QtGui.QPushButton('Refresh', self)
        refresh_btn.clicked.connect(self.refresh)
        #self.tools_box.addWidget(refresh_btn)

    def reset_window_layout(self):
        """
        This method puts all of the dock windows containing plots back into their original positions
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        self.integration_dock.setFloating(False)
        self.img_dock.setFloating(False)
        #self.plot_dock.setFloating(False)
        self.waterfall_dock.setFloating(False)

    def add_func(self, func):
        """adds an arbitrary function to the function dictionary

        the function should have the argument arr for a 2d image array

        Parameters
        ----------
        func : function
            the function to be passed in
        """
        if hasattr(func, '__iter__'):
            for fun in func:
                self.func_dict[fun.__name__] = fun
        else:
            self.func_dict[func.__name__] = func

    def remove_func(self, func_name):
        """This function will remove a function from the function dictionary

            To delete the name of the function must match the name of a function currently in the dictionary

            Parameters
            ----------

            func_name : str
                the name of the function to be removed. best to use func.__name__

            """

        try:
            self.data_dict.__delitem__(func_name)
        except KeyError:
            print("There is no function matching " + func_name + " in the function dictionary")


def main():
    """
    This allow the GUI to be run if the program is called as a file

    Returns
    -------
    None

    """
    app = QtGui.QApplication(sys.argv)
    viewer = Display()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
