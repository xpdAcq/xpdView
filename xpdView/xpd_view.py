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

from PyQt4 import QtGui, QtCore
import sys
import numpy as np
from xpdView.Tif_File_Finder import TifFileFinder
from xpdView.azimuthal import Azimuthal
from xpdView.plot_analysis import ReducedRepPlot
from xpdView.one_dimensional_int import IntegrationPlot
from xpdView.waterfall_maker import WaterFallMaker
from xpdView.waterfall_2d import Waterfall2D
from xpdView.peak_finding import PeakPlot
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolBar
import matplotlib.pyplot as plt
from xray_vision.messenger.mpl.cross_section_2d import CrossSection2DMessenger


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
    """
    This class contains all of the GUI information

    Attributes
    ----------
    analysis_type : string
            determines what kind of statistical parameter will be observed
    file_path : string
        the directory that will contain the .tif and .chi files for viewing
    key_list : list of strings
        that are ordered according to time data was read in for data_dict
    int_key_list : list of strings
        that show when integrated data was read in
    Tif : instance of the TifFileFinder class
        that is used to search and read in tif files
    Azi : instance of the Azimuthal class
        this class is used to integrate the 2D data as it is read in
    surface : Bool
        this variable keeps track of whether the user wants a contour plot or a wire plot in the 3d frame
    three_dim_drawn : Bool
        this variable keeps track of whether or not the 3d plot has been drawn yet
    data_dict : dictionary
        stores all of the 2D image arrays as a dictionary
    int_data_dict : dictionary
        stores all of the integrated data's x and y lists in a dictionary
    is_main_rpp_plotted : bool
        this variable keeps track of whether or not the main reduced rep plot has been created
    messenger : object
        this is an instance of the 2D cross section messenger class
    rpp_list : list of objects
        this list contains references to all of the reduced representation plots for when they update
    three_dim_list : list of objects
        this list contains references to all of the three dimensional plots for when they update
    peak_plots : list of objects
        this list contains references to all created peak plots (eventually all 1D reduced rep plots)
    plot_dock : object
        this object creates the floating window to hold the reduced representation plot
    img_dock : object
        this object creates the floating window to hold the image along with the cross section windows
    integration_dock : object
        this object creates the floating window to hold the 1D integrated data
    waterfall_dock : object
        this object creates the floating window to hold the 3D image with all the data sets
    fig1 : matplotlib figure
        this allows us to change the kinds of plots shown on any of the four tiles
    canvas1 : matplotlib canvas
        see reasoning above
    (same for 2 - 4)
    name_label : object
        widget that will display current final, UID, etc.
    img_slider : object
        makes slider for toolbar to change image
    img_spin : object
        creates spinbox that will be used to display current frame and allow more controlled steps through frames
    color : object
        combobox that will control color maps available to the user for the 2D data
    int_style : object
        combobox that contains options for controlling the intensity of the image
    int_min : object
        spinbox that will control the minimum intensity value
    int_max : object
        spinbox that will control the maximum intensity value
    tools_box : object
        creates the toolbar that will hold all of the other widgets
    rpp : None
        allows instance of the ReducedRepPlot later in the code
    one_dim_plot : None
        allows instance of IntegratedPlot class later in code
    water : None
        allows instance of Waterfall2D class later in code
    """

    def __init__(self):
        """
        This class creates the display window that is used by users to analyze their data

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
        self.analysis_type = None
        self.file_path = None
        data_list, self.key_list = data_gen(1)
        self.int_key_list = []
        self.Tif = TifFileFinder()
        self.Azi = Azimuthal()
        self.surface = True
        self.three_dim_drawn = False
        self.int_data_dict = dict()

        self.setDockNestingEnabled(True)
        self.setAnimated(True)

        # This sets up all we need from the cross section 2D messenger class for use in the code
        self.messenger = CrossSection2DMessenger(data_list=data_list,
                                                 key_list=self.key_list)
        self.display = self.messenger._display
        self.ctrls = self.messenger._ctrl_widget
        self.ctrls.set_image_intensity_behavior('full range')
        self.messenger.sl_update_image(0)
        self.data_dict = self.messenger._view._data_dict

        # These lists will contain references to the pop up plots so that they can be updated
        self.rpp_list = list()
        self.three_dim_list = list()
        self.peak_plots = list()

        self.func_dict = {np.std.__name__: np.std, np.mean.__name__: np.mean, np.amin.__name__: np.amin,
                          np.amax.__name__: np.amax, np.sum.__name__: np.sum}
        self.setDockNestingEnabled(True)
        self.setAnimated(True)

        # setting up dockable windows
        self.plot_dock = QtGui.QDockWidget("Dockable", self)
        self.plot_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.plot_dock.setWindowTitle("Reduced Representation")

        self.img_dock = QtGui.QDockWidget("Dockable", self)
        self.img_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.img_dock.setWindowTitle("Image")

        self.integration_dock = QtGui.QDockWidget("Dockable", self)
        self.integration_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        self.integration_dock.setWindowTitle("Integration")

        self.waterfall_dock = QtGui.QDockWidget("Dockable", self)
        self.waterfall_dock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
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
        self.int_min = self.ctrls._spin_min
        self.int_max = self.ctrls._spin_max

        # These statements add the dock widgets to the GUI
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.img_dock)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.plot_dock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.integration_dock)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.waterfall_dock)

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
        self.r_rep_widget()
        self.one_dim_integrate()
        self.waterfall_2d()

    def r_rep_widget(self):
        """
        This class creates the figure and instance of the ReducedRepPlot that is used to create the plot in the
        top right corner

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        canvas.mpl_connect('button_press_event', self.click_handling)
        FigureCanvas.setSizePolicy(canvas, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(canvas)
        self.rpp_list.append(ReducedRepPlot(self.data_dict, self.key_list, fig, canvas, self.func_dict))
        toolbar = NavigationToolBar(canvas, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        self.plot_dock.setWidget(multi)

    def new_r_rep(self, selection, x_min, x_max, y_min, y_max):
        """This method will make a reduced representation graph in a new window


        Parameters
        ----------
        selection : str
            The name of the desired analysis function
        x_min : int
            the starting x value defined by the ROI
        x_max : int
            the stopping x value defined by the ROI
        y_min : int
            the starting y value defined by the ROI
        y_max : int
            the stopping y value defined by the ROI

        Returns
        -------
        None
        """
        try:
            popup_window = QtGui.QDialog(self)
            popup_window.setWindowTitle(selection)
            popup_window.setWindowModality(QtCore.Qt.NonModal)
            fig = plt.figure()
            canvas = FigureCanvas(fig)
            canvas.mpl_connect('button_press_event', self.click_handling)
            toolbar = NavigationToolBar(canvas, self)
            self.rpp_list.append(ReducedRepPlot(self.data_dict, self.key_list, fig, canvas, self.func_dict, selection))
            idx = len(self.rpp_list) - 1
            vbox = QtGui.QVBoxLayout()
            vbox.addStretch()
            vbox.addWidget(toolbar)
            vbox.addStretch()
            vbox.addWidget(canvas)
            popup_window.setLayout(vbox)
            popup_window.show()
            self.rpp_list[idx].x_start = x_min
            self.rpp_list[idx].x_stop = x_max
            self.rpp_list[idx].y_start = y_min
            self.rpp_list[idx].y_stop = y_max
            self.rpp_list[idx].show()
            popup_window.exec_()
        except Exception:
            print("error creating a new rpp window")
        finally:
            self.rpp_list.__delitem__(idx)

    def update_r_rep(self, new_data):
        """This method updates the reduced representation graphs when there are new files present

        Parameters
        ----------
        new_data : list
            a list of new images

        Returns
        -------

        """
        for plot in self.rpp_list:
            plot.show(new_data=new_data)

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
        FigureCanvas.setSizePolicy(self.canvas3, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self.canvas3)
        self.one_dim_plot = IntegrationPlot(self.int_data_dict, self.fig3, self.canvas3)
        toolbar = NavigationToolBar(self.canvas3, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas3)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        self.integration_dock.setWidget(multi)

    def waterfall_3d(self, plot_type):
        """
        This method simply creates an instance of the class that creates the waterfall plot in the bottom right corner
        Parameters
        ----------
        self
        plot_type : str
            name of 3d plot type to use

        Returns
        -------
        None

        """
        window = QtGui.QDialog(self)
        window.setWindowTitle(plot_type)
        window.setWindowModality(QtCore.Qt.NonModal)
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolBar(canvas, self)
        water = WaterFallMaker(fig, canvas, self.int_data_dict, self.int_key_list)
        water.get_right_shape()
        x = plot_type
        self.three_dim_list.append([water, x])

        if plot_type is "surface":
            water.get_surface_plot()
        elif plot_type is "wire":
            water.get_wire_plot()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        window.setLayout(layout)
        window.show()
        window.exec_()

    def update_waterfall_3d(self):
        """
        This method simply updates all of the 3d plots
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        for thing in self.three_dim_list:
            if thing[1] == 'surface':
                thing[0].get_right_shape()
                thing[0].get_surface_plot()
            else:
                thing[0].get_right_shape()
                thing[0].get_wire_plot()

    def peak_plot(self):
        """
        This method creates a plot that allows the user to see the x location of all major peaks found in the integrated
        data

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        window = QtGui.QDialog(self)
        window.setWindowTitle('Peak Locations')
        window.setWindowModality(QtCore.Qt.NonModal)
        fig = plt.figure()
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolBar(canvas, self)
        canvas.mpl_connect('button_press_event', self.click_handling)
        peak_graph = PeakPlot(fig, canvas, self.int_data_dict, self.int_key_list)
        self.peak_plots.append(peak_graph)

        peak_graph.get_plot()

        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        window.setLayout(layout)
        window.show()
        window.exec_()

    def update_peak_plots(self, new_keys, new_x, new_y):
        """
        This method will update any of the peak plots that were created
        Parameters
        ----------
        new_keys : list of strings
            list of strings that contain the identifiers for the plots they represent
        new_x : list of 1d numpy arrays
            new data to be searched through
        new_y : list of 1d numpy arrays
            new data to be search through

        Returns
        -------
        None

        """
        for plot in self.peak_plots:
            plot.update_the_plot(new_keys, new_x, new_y)

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
        self.water = Waterfall2D(self.int_key_list, self.int_data_dict, fig, canvas)
        self.water.y_offset = .5
        toolbar = NavigationToolBar(canvas, self)
        self.water.generate_waterfall()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        self.waterfall_dock.setWidget(multi)

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
        setpath.triggered.connect(self.set_path)

        # sets up menu refresh option
        refresh_path = QtGui.QAction('&Refresh', self)
        refresh_path.setShortcut('Ctrl+R')
        refresh_path.triggered.connect(self.refresh)

        # This sets up the option that makes the popup window for reduced rep plot settings
        plt_action = QtGui.QAction("&Plot", self)
        plt_action.setShortcut("Ctrl+P")
        plt_action.triggered.connect(self.set_graph_settings)

        # This sets ups the option that makes the peak searching plot
        peak_action = QtGui.QAction("&Find Peaks", self)
        peak_action.setShortcut("Ctrl+F")
        peak_action.triggered.connect(self.peak_plot)

        # This sets up the options that control the waterfall 2d settings and 3d waterfall creation
        surface_action = QtGui.QAction("&Surface", self)
        surface_action.triggered.connect(lambda: self.waterfall_3d("surface"))

        twod_action = QtGui.QAction("&Show 2D Waterfall Toolbar", self)
        twod_action.triggered.connect(self.twod_plot_settings)

        wire_action = QtGui.QAction("&Wire", self)
        wire_action.triggered.connect(lambda: self.waterfall_3d("wire"))

        # This creates the window redocking option in the code
        reset_windows = QtGui.QAction('&Redock Windows', self)
        reset_windows.triggered.connect(self.reset_window_layout)

        # This sets up all of the menu widgets that are used in the GUI
        mainmenu = self.menuBar()
        window_menu = mainmenu.addMenu("&Window")
        filemenu = mainmenu.addMenu("&File")
        graph_menu = mainmenu.addMenu('&Reduced Representation')
        waterfall_menu = mainmenu.addMenu('&Waterfall Plots')
        filemenu.addAction(setpath)
        filemenu.addAction(refresh_path)
        graph_menu.addAction(plt_action)
        graph_menu.addAction(peak_action)
        waterfall_menu.addAction(surface_action)
        waterfall_menu.addAction(wire_action)
        waterfall_menu.addAction(twod_action)
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
        for widget in [y_offset_label, y_offset_slider, x_offset_label, x_offset_slider, normalize_option_label, normalize_option_box]:
            layout.addStretch()
            layout.addWidget(widget)

        settings_window.setLayout(layout)
        settings_window.show()
        settings_window.exec_()

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
        min_label.setText('Int Min')
        self.tools_box.addWidget(min_label)
        self.tools_box.addWidget(self.int_min)
        max_label = QtGui.QLabel()
        max_label.setText('Int Max')
        self.tools_box.addWidget(max_label)
        self.tools_box.addWidget(self.int_max)

        # This makes the Label that is used to display the current key name
        self.name_label.setText('Current File: ' + self.key_list[0])
        self.tools_box.addWidget(self.name_label)

        # This makes sure that the display is updated when the image is changed
        self.img_spin.valueChanged.connect(self.change_frame)

        # This makes the refresh button
        refresh_btn = QtGui.QPushButton('Refresh', self)
        refresh_btn.clicked.connect(self.refresh)
        self.tools_box.addWidget(refresh_btn)

    def change_frame(self, val):
        """
        This method takes care of changing the int_plot along with the file name being displayed
        Parameters
        ----------
        val : int
            the value that comes in from the widget

        Returns
        -------
        None

        """
        self.one_dim_plot.give_plot(self.key_list[val])
        self.name_label.setText(self.key_list[val])

    def set_integration_parameters(self):
        """
        This method provides the user to check if the integration parameters to be used are correct
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        # This sets up the initial parameters for the popup window
        popup = QtGui.QDialog(self)
        popup.setWindowTitle('Integration Parameters')
        wavelength = 0.184320
        poni1 = .1006793
        poni2 = .1000774
        dist = 0.2418217
        rot1 = 0
        rot2 = 0
        vbox = QtGui.QVBoxLayout()
        popup.setLayout(vbox)

        # This sets up  the line for setting the wavelength
        hbox1 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox1)
        wave_label = QtGui.QLabel()
        wave_label.setText('Wavelength (in Angstroms): ')
        wave_number = QtGui.QDoubleSpinBox()
        wave_number.setDecimals(8)
        wave_number.setValue(wavelength)
        hbox1.addWidget(wave_label)
        hbox1.addWidget(wave_number)

        # This sets up the line for setting the poni1 values
        hbox2 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox2)
        poni1_label = QtGui.QLabel()
        poni1_label.setText('Poni1: ')
        poni1_number = QtGui.QDoubleSpinBox()
        poni1_number.setDecimals(8)
        poni1_number.setValue(poni1)
        hbox2.addWidget(poni1_label)
        hbox2.addWidget(poni1_number)

        # This sets up the line for setting the poni2 values
        hbox3 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox3)
        poni2_label = QtGui.QLabel()
        poni2_label.setText('Poni2: ')
        poni2_number = QtGui.QDoubleSpinBox()
        poni2_number.setDecimals(8)
        poni2_number.setValue(poni2)
        hbox3.addWidget(poni2_label)
        hbox3.addWidget(poni2_number)

        # This sets up the line for setting the distance value
        hbox4 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox4)
        dist_label = QtGui.QLabel()
        dist_label.setText('Distance (m): ')
        dist_number = QtGui.QDoubleSpinBox()
        dist_number.setValue(dist)
        dist_number.setDecimals(8)
        hbox4.addWidget(dist_label)
        hbox4.addWidget(dist_number)

        # This sets up the line for setting the rot1 value
        hbox5 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox5)
        rot1_label = QtGui.QLabel()
        rot1_label.setText('Rotation 1 (Radians): ')
        rot1_number = QtGui.QDoubleSpinBox()
        rot1_number.setValue(rot1)
        rot1_number.setDecimals(8)
        hbox5.addWidget(rot1_label)
        hbox5.addWidget(rot1_number)

        # This sets up the line for setting the rot2 value
        hbox6 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox6)
        rot2_label = QtGui.QLabel()
        rot2_label.setText('Rotation 2 (Radians): ')
        rot2_number = QtGui.QDoubleSpinBox()
        rot2_number.setValue(rot2)
        rot2_number.setDecimals(8)
        hbox6.addWidget(rot2_label)
        hbox6.addWidget(rot2_number)

        # This sets up the button to accept the values and close the window
        hbox6 = QtGui.QHBoxLayout()
        vbox.addLayout(hbox6)
        accept_btn = QtGui.QPushButton()
        accept_btn.setText('Accept')
        hbox6.addWidget(accept_btn)
        accept_btn.clicked.connect(popup.close)
        accept_btn.clicked.connect(lambda: self.Azi.set_integration_parameters(wl=wave_number.value(),
                                                                               poni1=poni1_number.value(),
                                                                               poni2=poni2_number.value(),
                                                                               dist=dist_number.value(),
                                                                               rot1=rot1_number.value(),
                                                                               rot2=rot2_number.value()))

        popup.show()
        popup.exec_()

    def set_path(self):
        """
        This creates the dialog window that pops up to set the path

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        popup = QtGui.QFileDialog()
        self.file_path = str(popup.getExistingDirectory())
        self.Tif._directory_name = self.file_path
        self.set_integration_parameters()
        self.Tif.get_file_list()
        self.Azi.get_right_names(self.Tif.file_list, self.Tif.pic_list)

        if len(self.Tif.pic_list) == 0:
            print('No .tif files in directory')
        else:
            x = self.key_list[0]
            if x == '0':
                del self.data_dict[self.key_list[0]]
                self.key_list.remove(x)
                self.update_int_data(self.Azi.file_names, self.Azi.x_lists, self.Azi.y_lists)
                self.update_data(self.Tif.pic_list, self.Tif.file_list)
                self.messenger.sl_update_image(0)
                self.one_dim_plot.give_plot(self.key_list[0])
                self.name_label.setText(self.key_list[0])
            else:
                self.update_int_data(self.Azi.file_names, self.Azi.x_lists, self.Azi.y_lists)
                self.update_data(self.Tif.pic_list, self.Tif.file_list)

    def refresh(self):
        """
        This method checks for new data using the methods available to ChiFileFinder and TifFileFinder Classes and
        handles the new data to ensure that nothing breaks

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        new_file_names, new_data = self.Tif.get_new_files()
        int_new_files, int_data_x, int_data_y = self.Azi.refresh_time(new_file_names, new_data)
        if len(new_file_names) == 0 and len(int_new_files) == 0:
            print("No new files found")
        elif len(new_file_names) == 0 and len(int_new_files) != 0:
            self.update_int_data(int_new_files, int_data_x, int_data_y)
            self.update_data([], [])
            self.update_waterfall_3d()
            self.update_peak_plots(int_new_files, int_data_x, int_data_y)
        elif len(new_file_names) != 0 and len(int_new_files) == 0:
            self.update_data(new_data, new_file_names)
            self.update_r_rep(new_data)
        else:
            self.update_int_data(int_new_files, int_data_x, int_data_y)
            self.update_data(new_data, new_file_names)
            self.update_waterfall_3d()
            self.update_peak_plots(int_new_files, int_data_x, int_data_y)
            self.update_r_rep(new_data)

    def update_data(self, data_list, file_list):
        """
        This method updates the data_dict for the viewer and rest of the program to use

        Parameters
        ----------
        self
        data_list : list of 2D arrays
            data that is to be put into the dictionary
        file_list : list of stings
            unique key names associated with the 2D arrays

        Returns
        -------
        None

        """
        old_length = len(self.key_list)
        for file in file_list:
            self.key_list.append(file)
        for i in range(old_length, len(self.key_list)):
            self.data_dict[self.key_list[i]] = data_list[i - old_length]
        self.img_slider.setMaximum(len(self.key_list) - 1)
        self.img_spin.setMaximum(len(self.key_list) - 1)

    def update_int_data(self, file_list, data_x, data_y):
        """
        This method update the integrated data dictionary

        Parameters
        ----------
        self
        file_list : list of strings
            key names that are the same as the 2D arrays but associated with the 1D plots
        data_x : list of 1D numpy arrays
            x-axis data for the 1D plot associated with corresponding key name
        data_y : list of 1D numpy arrays
            y-axis data for the 1D plot associated with corresponding key name

        Returns
        -------
        None

        """
        old_length = len(self.int_key_list)
        for file in file_list:
            self.int_key_list.append(file)
        for i in range(old_length, len(self.int_key_list)):
            self.int_data_dict[self.int_key_list[i]] = [data_x[i - old_length], data_y[i - old_length]]
        if len(self.int_key_list) != 0:
            self.water.normalize_data()
            self.water.generate_waterfall()

    def get_three_dim_plot(self):
        """
        This method simply draws the kind of plot selected by the user
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        if self.surface:
            self.water.get_surface_plot()
        else:
            self.water.get_wire_plot()

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
        self.plot_dock.setFloating(False)
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
