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
    This function generates circular data to create the homepage, and also to practice with

    Parameters
    ----------
    length: some integer that will decide the length of the data and key arrays

    Returns
    -------
    data: a list of 2-D numpy arrays; normally only generates one to make the homepage
    keys: a list of strings that represent the indices of the generated arrays

    """
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

    def __init__(self):
        """
        This class creates the display window that is used by users to analyze their data

        Parameters
        ----------
        none

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
        messenger : creates an instance of the CrossSection2DMessenger widget
            for future use in code
        ctrls : object
            spawns all of the widgets made available by the CrossSection2DMessenger class
        data_dict : dictionary
            stores all of the 2D image arrays as a dictionary
        int_data_dict : dictionary
            stores all of the integrated data's x and y lists in a dictionary
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
        name_label : object
            widget that will display current final, UID, etc.
        rpp : None
            allows instance of the ReducedRepPlot later in the code
        one_dim_plot : None
            allows instance of IntegratedPlot class later in code
        water : None
            allows instance of WaterfallMaker class later in code

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

        # These commands initialize the 2D cross section widget to draw itself
        self.messenger = CrossSection2DMessenger(data_list=data_list,
                                                 key_list=self.key_list)
        self.ctrls = self.messenger._ctrl_widget
        self.ctrls.set_image_intensity_behavior('full range')
        self.messenger.sl_update_image(0)
        self.data_dict = self.messenger._view._data_dict
        self.int_data_dict = dict()

        # This makes the layout for the main window
        self.frame = QtGui.QFrame()
        self.main_layout = QtGui.QVBoxLayout()
        self.frame.setLayout(self.main_layout)
        self.setCentralWidget(self.frame)
        self.display = self.messenger._display
        # This makes the first layer for the
        self.display_box_1 = QtGui.QHBoxLayout()
        self.display_box_1.addWidget(self.display)
        self.display_box_2 = QtGui.QHBoxLayout()
        self.tools_box = QtGui.QHBoxLayout()
        self.main_layout.addLayout(self.display_box_1)
        self.main_layout.addLayout(self.display_box_2)
        self.main_layout.addLayout(self.tools_box)

        # These methods will set up the menu bars and the tool bars
        self.name_label = QtGui.QLabel()
        self.set_up_tool_bar()
        self.set_up_menu_bar()

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
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        canvas.mpl_connect('button_press_event', self.click_handling)
        FigureCanvas.setSizePolicy(canvas, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(canvas)
        canvas.setMinimumWidth(500)
        self.rpp = ReducedRepPlot(self.data_dict, self.key_list, 0, 100, 0, 100, "min", figure, canvas)
        toolbar = NavigationToolBar(canvas, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.display_box_1.addStretch()
        self.display_box_1.addLayout(layout)

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
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        FigureCanvas.setSizePolicy(canvas, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(canvas)
        canvas.setMinimumHeight(200)
        self.one_dim_plot = IntegrationPlot(self.int_data_dict, self.key_list, figure, canvas)
        toolbar = NavigationToolBar(canvas, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.display_box_2.addStretch()
        self.display_box_2.addLayout(layout)

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
        figure = plt.figure()
        canvas = FigureCanvas(figure)
        canvas.setMinimumHeight(200)
        FigureCanvas.setSizePolicy(canvas, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(canvas)
        self.water = WaterFallMaker(figure, canvas, self.int_data_dict, self.int_key_list)
        toolbar = NavigationToolBar(canvas, self)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(canvas)
        self.display_box_2.addStretch()
        self.display_box_2.addLayout(layout)

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
            self.ctrls._slider_img.setValue(int(event.xdata))

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

        # This sets up all of the menu widgets that are used in the GUI
        mainmenu = self.menuBar()
        filemenu = mainmenu.addMenu("&File")
        graph_menu = mainmenu.addMenu('&Reduced Representation')
        three_dim = mainmenu.addMenu('&3D Plot style')
        filemenu.addAction(setpath)
        filemenu.addAction(refresh_path)
        graph_menu.addAction(plt_action)
        three_dim.addAction(surface_action)
        three_dim.addAction(wire_action)

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
        self.analysis_type = list(self.rpp.func_dict.keys())[i]

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
            self.rpp.x_start = x_min
            self.rpp.x_stop = x_max
            self.rpp.y_start = y_min
            self.rpp.y_stop = y_max
            self.rpp.selection = self.analysis_type
            self.rpp.analyze()
            self.rpp.show()
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
        analysis_selector.addItems(list(self.rpp.func_dict.keys()))

        print(self.messenger._fig.axes[0].get_xlim())
        print(self.messenger._fig.axes[0].get_ylim())

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

        menu.setLayout(vbox)
        menu.show()
        menu.exec_()

    def set_up_tool_bar(self):
        """
        This creates all of the widgets that are put into the toolbar and puts them in there

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        # All these commands will extract the desired widgets from x-ray_vision for our purposes
        self.tools_box.addWidget(self.ctrls._slider_img)
        self.tools_box.addWidget(self.ctrls._spin_img)
        self.tools_box.addWidget(self.ctrls._cm_cb)
        self.tools_box.addWidget(self.ctrls._cmbbox_intensity_behavior)
        min_label = QtGui.QLabel()
        min_label.setText('Int Min')
        self.tools_box.addWidget(min_label)
        self.tools_box.addWidget(self.ctrls._spin_min)
        max_label = QtGui.QLabel()
        max_label.setText('Int Max')
        self.tools_box.addWidget(max_label)
        self.tools_box.addWidget(self.ctrls._spin_max)

        # This makes the Label that is used to display the current key name
        self.name_label.setText('Current File: '+self.key_list[0])
        self.tools_box.addWidget(self.name_label)
        # This makes sure that the display is updated when the image is changed
        self.ctrls._spin_img.valueChanged.connect(self.change_display_name)
        self.ctrls._slider_img.valueChanged.connect(self.change_one_dim_plot)

        # This makes the refresh button
        refresh_btn = QtGui.QPushButton('Refresh', self)
        refresh_btn.clicked.connect(self.refresh)
        self.tools_box.addWidget(refresh_btn)

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
            if x == 'Home' or x == '0':
                del self.data_dict[self.key_list[0]]
                self.key_list.remove(x)
                self.update_int_data(self.Chi.file_list, self.Chi.x_lists, self.Chi.y_lists)
                self.update_data(self.Tif.pic_list, self.Tif.file_list)
                self.messenger.sl_update_image(0)
                self.one_dim_plot.give_plot(self.ctrls._slider_img.value())
            else:
                self.update_int_data(self.Chi.file_list, self.Chi.x_lists, self.Chi.y_lists)
                self.update_data(self.Tif.pic_list, self.Tif.file_list)
                self.messenger.sl_update_image(0)
                self.one_dim_plot.give_plot(self.ctrls._slider_img.value())

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
            self.rpp.show(new_data=new_data)
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
            x = file.split('.')
            self.key_list.append(x[0])
        for i in range(old_length, len(self.key_list)):
            self.data_dict[self.key_list[i]] = data_list[i - old_length]
        self.ctrls._slider_img.setMaximum(len(self.key_list) - 1)
        self.ctrls._spin_img.setMaximum(len(self.key_list) - 1)

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
            x = file.split('.')
            self.int_key_list.append(x[0])
        for i in range(old_length, len(self.int_key_list)):
            self.int_data_dict[self.int_key_list[i]] = [data_x[i], data_y[i]]
        if len(self.int_key_list) != 0:
            self.water.get_right_shape()
            self.get_three_dim_plot()
            self.three_dim_drawn = True

    def change_display_name(self, index_val):
        """
        This method updates the displayed current key name on the tool bar

        Parameters
        ----------
        self
        index_val : int
            This is index of the key with the associated new image and 1D plot

        Returns
        -------
        None

        """
        self.name_label.setText("Current: " + self.key_list[index_val])

    def change_one_dim_plot(self, index_val):
        """
        This function updates the 1D plot for the user

        Parameters
        ----------
        self
        index_val : int
            Index value of the new plot that is supposed to be displayed

        Returns
        -------
        None

        """
        self.one_dim_plot.give_plot(index=index_val)

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


def main():
    app = QtGui.QApplication(sys.argv)
    viewer = Display2()
    viewer.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
