"""
This file will contain the code that makes the XPD view GUI
"""
import os
import sys
from functools import partial
from collections import Iterable

import numpy as np
from tifffile import imread

import matplotlib
matplotlib.use('qt5Agg')
from matplotlib.figure import Figure
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import\
        FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import\
        NavigationToolbar2QT as NavigationToolBar

# classes for plotting
from xpdview.cross_2d import CrossSection, StackViewer
from xpdview.waterfall import Waterfall
from xpdview.utils import chi_read, load_files

# top definitions for IO handlers
TIF_READER = partial(imread)
NPY_READER = partial(np.load)
CHI_READER = partial(chi_read) # special as we still take fit2d
GR_READER = partial(np.loadtxt, skiprows=27)  # skiprows=27 -> xPDFsuite

class XpdView(QtWidgets.QMainWindow):
    def __init__(self, filepath=None):
        """
        top-level class to configure GUI and holds 2d/1d data
        visualization classes. Note all the data are carried by
        visualization classes, not by this GUI class.

        Parameters
        ----------
        filepath : str, optional
            filepath when using filebased operation. default to
            user home directory

        Attributes
        ----------
        img_data_ext : str, optional
            extention of 2d image data will be read. options are '.tif'
            or '.npy'. default to '.tif'
        int_data_ext : str, optional
            extention of 1d reduced data will be read. options are
            '.chi' or '.gr'. default to '.chi'
        img_handler : object
            function to load 2d image from different library options
            are tifffile.imread or numpy.load. default to tifffile.imread
        viewer : xpdView.cross2d.StackViewer
            instance of 2d stack viewer which carries key_list and
            img_data_list
        waterfall : xpdView.waterfall.Waterfall
            instance of waterfall plotting class which carries key_list
            and int_data_list
        """
        # configure QT property
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('XPD View')
        self.setDockNestingEnabled(True)
        self.setAnimated(False)
        if not filepath:
            filepath=os.path.expanduser('~')
        self.filepath = filepath
        self.img_data_ext = '.tif'
        self.int_data_ext = '.chi'
        self.img_handler = TIF_READER  # default to tifffile.imread
        self.int_data_handler = CHI_READER
        self.int_data_prefix = 'Q_'  # NO ROOM FOR CHANGE, HAHAHA

        # init mpl figures and canvas for plotting
        self.img_fig = Figure(tight_layout=True)
        self.img_canvas = FigureCanvas(self.img_fig)
        self.img_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)
        # core 2d viewer
        self._viewer = CrossSection(self.img_fig, cmap='CMRmap')
        # stack viwer
        self.viewer = StackViewer(self._viewer)

        self.waterfall_fig = Figure(tight_layout=False)
        self.waterfall_canvas = FigureCanvas(self.waterfall_fig)
        self.waterfall_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                            QtWidgets.QSizePolicy.Expanding)
        self.waterfall = Waterfall(self.waterfall_fig, self.waterfall_canvas)
        self.water_ax = self.waterfall.ax
        self._default_plot(self.water_ax)

        # create 1d plot axes in place
        self.int_fig = Figure(tight_layout=True)
        self.int_canvas = FigureCanvas(self.int_fig)
        self.int_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                      QtWidgets.QSizePolicy.Expanding)
        self.int_ax = self.int_fig.add_subplot(111)
        self.int_ax.set_autoscale_on(False)
        self._default_plot(self.int_ax)
        # link slider of image viewer with 1d plot
        self.viewer.slider.on_changed(self.update_one_dim_plot)

        # adding qt widgets
        self.img_dock = QtWidgets.QDockWidget("Dockable", self)
        self.img_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.img_dock.setWindowTitle("2D Image")
        self._configure_dock(self.img_dock, self.img_canvas)

        self.int_dock = QtWidgets.QDockWidget("Dockable", self)
        self.int_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.int_dock.setWindowTitle("1D Integration")
        self._configure_dock(self.int_dock,self.int_canvas)

        self.waterfall_dock = QtWidgets.QDockWidget("Dockable", self)
        self.waterfall_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable)
        self.waterfall_dock.setWindowTitle("Waterfall Plot")
        self._configure_dock(self.waterfall_dock, self.waterfall_canvas)

        # add gui buttons
        self.set_up_menu_bar()
        self.tools_box = QtWidgets.QToolBar()
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.tools_box)
        self.set_up_tool_bar()

        # These statements add the dock widgets to the GUI
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.img_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.int_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.waterfall_dock)

    def _configure_dock(self, qt_dock, canvas):
        """helper function to add mpl toolbar"""
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(NavigationToolBar(canvas, self))
        layout.addWidget(canvas)
        multi = QtWidgets.QWidget()
        multi.setLayout(layout)
        qt_dock.setWidget(multi)

    def _default_plot(self, ax):
        """method to display only text but not plot
        """
        ax.cla()
        ax.text(.5, .5,
                '{}'.format("xpdView is a part of xpdAcq workflow\n"
                            "it expects data generated from standard "
                            "pipeline.\nPlease go to our online "
                            "documentation for more details:\n"
                            "http://xpdacq.github.io/quickstart.html"),
                ha='center', va='center', color='w',
                transform= ax.transAxes, size=10)
        ax.set_facecolor('k')

    def update(self, key_list=None, img_data_list=None,
               int_data_list=None, refresh=False):
        """method to update data carried by class"""
        # key_list is required
        # call update methods of each class
        print("INFO: new key len = {}, img_data len = {}"
              .format(len(key_list), len(img_data_list)))
        # FIXME: detailed flag about update status in each class
        self.viewer.update(key_list, img_data_list, refresh)
        self.waterfall.update(key_list, int_data_list, refresh)
        # link callback again
        self.viewer.slider.on_changed(self.update_one_dim_plot)
        self.update_one_dim_plot(int(round(self.viewer.slider.val)))

    def set_path(self, refresh=False):
        """
        This creates the dialog window that pops up to set the path

        Parameters
        ----------
        refresh : bool, optional
            option to set as refresh or not
        """
        if not refresh:
            popup = QtWidgets.QFileDialog()
            self.filepath = popup.getExistingDirectory()
        fn_meta = load_files(self.filepath, self.img_data_ext,
                             self.int_data_ext, self.int_data_prefix)
        if not all(fn_meta):
            self.viewer.no_image_plot()
            # call update method to turn 2d and 1d plot into black screen
            self.waterfall.update([], [], True)
            self.update_one_dim_plot(0)
            return
        # unpack results
        img_key_list, operation_list, unit = fn_meta
        self.waterfall.unit = unit
        key_list = img_key_list  # always use key_list from img data
        img_data_list = []
        int_data_list = []
        for meta in operation_list:
            if not isinstance(meta, str):
                # iterable -> comes from zip(...)
                img_fn, int_fn = meta
                _array = self.int_data_handler(os.path.join(self.filepath,
                                                            int_fn))
                x = _array[:,0]
                y = _array[:,1]
                int_data_list.append((x, y))
            else:
                # always load img data
                img_fn = meta
            img_data_list.append(self.img_handler(os.path.join(self.filepath,
                                                               img_fn)))
        # file-based operation; always refresh
        self.update(key_list, img_data_list, int_data_list, True)

    def refresh(self):
        """method to reload files in current directory. it's basically a
        set_path method operates on filepath being set currently"""
        self.set_path(refresh=True)

    def update_one_dim_plot(self, val):
        """method to display auxiliary 1d plot"""
        # obtain state from waterfall plot class
        if self.waterfall.halt:
            # no int_data_list passed to update -> turn 1D fig to black
            self.waterfall.no_int_data_plot(self.int_ax, self.int_canvas)
            return
        else:
            # use the same rounding logic
            _val = int(round(val))
            int_data_list = self.waterfall.int_data_list
            key_list = self.waterfall.key_list
            _array = int_data_list[_val]
            x,y = _array
            self.int_ax.set_facecolor('w')
            self.int_ax.cla()
            xlabel, ylabel = self.waterfall.unit
            self.int_ax.set_xlabel(xlabel)
            self.int_ax.set_ylabel(ylabel)
            self.int_ax.plot(x,y)
            self.int_ax.set_title(key_list[_val], fontsize=10)
            self.int_canvas.draw_idle()

    ######## gui btns ##############
    def set_up_menu_bar(self):
        """
        This method creates the menu bar and ties all of the actions
        associated with the different options to the menu bar

        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        # set path option
        setpath = QtWidgets.QAction("&Set Directory", self)
        setpath.setShortcut("Ctrl+O")
        setpath.setStatusTip("Set image directory")
        setpath.triggered.connect(self.set_path)

        # sets up menu refresh option
        refresh_path = QtWidgets.QAction('&Refresh', self)
        refresh_path.setShortcut('Ctrl+R')
        refresh_path.triggered.connect(self.refresh)

        # This creates the window redocking option in the code
        reset_windows = QtWidgets.QAction('&Redock Windows', self)
        reset_windows.triggered.connect(self.reset_window_layout)

        # This sets up all of the menu widgets that are used in the GUI
        mainmenu = self.menuBar()
        filemenu = mainmenu.addMenu("&File")
        filemenu.addAction(setpath)
        filemenu.addAction(refresh_path)
        window_menu = mainmenu.addMenu("&Window")
        window_menu.addAction(reset_windows)

    def set_up_tool_bar(self):
        """
        This takes all of the widgets that are put into the toolbar
        puts them in there

        Returns
        -------
        None

        """
        # All these commands will add the widgets in
        refresh_btn = QtWidgets.QPushButton('Refresh', self)
        refresh_btn.clicked.connect(self.refresh)
        self.tools_box.addWidget(refresh_btn)

        img_data_ext_label = QtWidgets.QLabel('2D image file extention')
        self.img_data_ext_cbox = QtWidgets.QComboBox()
        self.img_data_ext_cbox.addItem(".tif")
        self.img_data_ext_cbox.addItem(".npy")
        self.img_data_ext_cbox.activated[str].\
                connect(self.change_img_data_ext)

        int_data_ext_label = QtWidgets.QLabel('1D reduced data file extention')
        self.int_data_ext_cbox = QtWidgets.QComboBox()
        self.int_data_ext_cbox.addItem(".chi")
        self.int_data_ext_cbox.addItem(".gr")
        self.int_data_ext_cbox.activated[str].\
                connect(self.change_int_data_ext)

        widget_list = [img_data_ext_label, self.img_data_ext_cbox,
                       int_data_ext_label, self.int_data_ext_cbox]
        for widget in widget_list:
            self.tools_box.addWidget(widget)

    def change_int_data_ext(self, txt):
        if self.int_data_ext_cbox.currentText() == '.chi':
            print("INFO: change 1d reduced data default extention to .chi")
            self.int_data_ext = '.chi'
            self.int_data_handler = CHI_READER
            self.refresh()
        elif self.int_data_ext_cbox.currentText() == '.gr':
            print("INFO: change 1d reduced data default extention to .gr")
            self.int_data_ext = '.gr'
            self.int_data_handler = GR_READER
            self.refresh()

    def change_img_data_ext(self, txt):
        if self.img_data_ext_cbox.currentText() == '.tif':
            print("INFO: change 2d img data default extention to .tif")
            self.img_data_ext = '.tif'
            self.img_handler = TIF_READER
            self.refresh()

        elif self.img_data_ext_cbox.currentText() == '.npy':
            print("INFO: change 2d img data default extention to .npy")
            self.img_data_ext = '.npy'
            self.img_handler = NPY_READER
            self.refresh()

    def reset_window_layout(self):
        """This method puts all of the dock windows containing plots
        back into their original positions
        """
        self.int_dock.setFloating(False)
        self.img_dock.setFloating(False)
        self.waterfall_dock.setFloating(False)
