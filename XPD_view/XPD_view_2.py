"""
This file will contain the code that makes the XPD view GUI
"""

from PyQt4 import QtGui, QtCore
import sys
import numpy as np
from Tif_File_Finder import TifFileFinder
from Chi_File_Finder import ChiFileFinder
from plot_analysis import ReducedRepPlot
from one_dimensional_int import IntegrationPlot
from waterfall_maker import WaterFallMaker
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
                if x == int(x_length/2) and y == int(y_length/2):
                    array_style[x][y] = 0
                else:
                    array_style[x][y] = height/np.sqrt((x-int(x_length/2))**2+(y-int(y_length/2))**2)
        data.append(array_style)
    return data, keys


class Display2(QtGui.QMainWindow):
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
        Chi : instance of the ChiFileFinder class
            that is used to search and read in chi files
        surface : Bool
            this variable keeps track of whether the user wants a contour plot or a wire plot in the 3d frame
        three_dim_drawn : Bool
            this variable keeps track of whether or not the 3d plot has been drawn yet
        data_dict : dictionary
            stores all of the 2D image arrays as a dictionary
        int_data_dict : dictionary
            stores all of the integrated data's x and y lists in a dictionary
        messenger : object
            this is an instance of the 2D cross section messenger class
        plot_dock : object
            this object creates the floating window to hold the reduced representation plot
        img_dock : object
            this object creates the floating window to hold the image along with the cross section windows
        integration_dock : object
            this object creates the floating window to hold the 1D integrated data
        waterfall_dock : object
            this object creates the floating window to hold the 3D image with all the data sets
        frame : object
            creates the background frame on which all of the widgets are displayed
        main_layout : object
            creates main vertical box that will store all display widgets and tools
        display_box_1 : object
            creates the horizontal box intended to contain the 2D cross section widget and some other plot
        display_box_2 : object
            creates the horizontal box that will hold two other useful plots
        tools_box : object
            creates the horizontal box that will contain all of the control widgets
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
            allows instance of WaterfallMaker class later in code
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
        self.Chi = ChiFileFinder()
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

        self.rpp_list = list()
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

        self.int_data_dict = dict()
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
        self.waterfall()

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
        """

        Parameters
        ----------
        new_data

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

    def waterfall(self):
        """
        This method simply creates an instance of the class that creates the waterfall plot in the bottom right corner
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        FigureCanvas.setSizePolicy(self.canvas4, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self.canvas4)
        self.water = WaterFallMaker(self.fig4, self.canvas4, self.int_data_dict, self.int_key_list)
        toolbar = NavigationToolBar(self.canvas4, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas4)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        self.waterfall_dock.setWidget(multi)

    def click_handling(self, event):
        """
        This method simply tells the display window what to do when someone clicks on the top right tile what to do

        Parameters
        ----------
        event: object
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

        # This sets up the option that makes the popup window
        plt_action = QtGui.QAction("&Plot", self)
        plt_action.setShortcut("Ctrl+P")
        plt_action.triggered.connect(self.set_graph_settings)

        # This sets up the options that control the 3d Plot style
        surface_action = QtGui.QAction("&Surface", self)
        surface_action.triggered.connect(self.surface_plot_wanted)

        wire_action = QtGui.QAction("&Wire", self)
        wire_action.triggered.connect(self.wire_plot_wanted)

        reset_windows = QtGui.QAction("&Reset Window Layout", self)
        reset_windows.triggered.connect(self.reset_window_layout)

        # This sets up all of the menu widgets that are used in the GUI
        mainmenu = self.menuBar()
        window_menu = mainmenu.addMenu("&Window")
        filemenu = mainmenu.addMenu("&File")
        graph_menu = mainmenu.addMenu('&Reduced Representation')
        three_dim = mainmenu.addMenu('&3D Plot style')
        filemenu.addAction(setpath)
        filemenu.addAction(refresh_path)
        graph_menu.addAction(plt_action)
        three_dim.addAction(surface_action)
        three_dim.addAction(wire_action)
        window_menu.addAction(reset_windows)

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
        menu.setWindowModality(QtCore.Qt.ApplicationModal)
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

        Parameters
        ----------
        val

        Returns
        -------

        """
        self.one_dim_plot.give_plot(self.key_list[val])
        self.name_label.setText(self.key_list[val])

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
        self.Chi._directory_name = self.file_path
        self.Tif.get_file_list()
        self.Chi.get_file_list()
        if len(self.Tif.pic_list) == 0:
            print('No .tif files in directory')
        else:
            x = self.key_list[0]
            if x == '0':
                del self.data_dict[self.key_list[0]]
                self.key_list.remove(x)
                self.update_int_data(self.Chi.file_list, self.Chi.x_lists, self.Chi.y_lists)
                self.update_data(self.Tif.pic_list, self.Tif.file_list)
                self.messenger.sl_update_image(0)
                self.one_dim_plot.give_plot(self.key_list[0])
                self.name_label.setText(self.key_list[0])
            else:
                self.update_int_data(self.Chi.file_list, self.Chi.x_lists, self.Chi.y_lists)
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
        int_new_files, int_data_x, int_data_y = self.Chi.get_new_files()
        if len(new_file_names) == 0 and len(int_new_files) == 0:
            print("No new files found")
        elif len(new_file_names) == 0 and len(int_new_files) != 0:
            self.update_int_data(int_new_files, int_data_x, int_data_y)
            self.update_data([], [])
        elif len(new_file_names) != 0 and len(int_new_files) == 0:
            self.update_data(new_data, new_file_names)
            self.update_r_rep(new_data)
        else:
            self.update_int_data(int_new_files, int_data_x, int_data_y)
            self.update_data(new_data, new_file_names)

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
            self.int_data_dict[self.int_key_list[i]] = [data_x[i-old_length], data_y[i-old_length]]
        if len(self.int_key_list) != 0:
            self.water.get_right_shape()
            self.get_three_dim_plot()
            self.three_dim_drawn = True

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

    def surface_plot_wanted(self):
        """
        This function simply allows the 3d style options to draw the right plot

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        self.surface = True
        if self.three_dim_drawn:
            self.get_three_dim_plot()

    def wire_plot_wanted(self):
        """
        This function allows the 3d style option to draw the wire option

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        self.surface = False
        if self.three_dim_drawn:
            self.get_three_dim_plot()

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

    def set_func_dict(self, func_list):
        """a setter for func_dict that takes in a list of functions

        creates a dictionary for them
        functions should have the arguments
        arr for the 2d image array

        Parameters
        ----------
        func_list : a list of functions that you want to replace the current dictionary functions
        """
        self.func_dict.clear()
        for func in func_list:
            self.func_dict[func.__name__] = func

    def add_func(self, func):
        """adds an arbitrary function to the function dictionary

        the function should have the argument arr for a 2d image array

        Parameters
        ----------
        func : function
            the function to be passed in
        """
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
    viewer = Display2()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
