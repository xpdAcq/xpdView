"""
This file will contain the code that makes the XPD view GUI
"""
import sys
import os
import numpy as np
from tifffile import imread

# FIXME: update qt5 if it's fully compatible
from PyQt4 import QtGui, QtCore
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolBar

# classes for plotting
from xpdView.cross_2d import CrossSection, StackViewer
from xpdView.waterfall import Waterfall

class XpdView(QtGui.QMainWindow):
    def __init__(self, filepath=None):
        """
        top-level GUI holds 2d/1d data visualization class

        Parameters
        ----------
        filepath : str, optional
            default filepath when using filebased operation. default to
            user home directory
        """
        # configure QT property
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('XPD View')
        self.setDockNestingEnabled(True)
        self.setAnimated(False)
        if not filepath:
            filepath=os.path.expanduser('~')
        self.filepath = filepath

        # init mpl figures and canvas for plotting
        self.img_fig = Figure(tight_layout=True)
        self.img_canvas = FigureCanvas(self.img_fig)
        self.img_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
        self._viewer = CrossSection(self.img_fig) # core 2d viewer
        self.viewer = StackViewer(self._viewer) # stack viwer

        self.waterfall_fig = Figure(tight_layout=True)
        self.waterfall_canvas = FigureCanvas(self.waterfall_fig)
        self.waterfall_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                            QtGui.QSizePolicy.Expanding)
        self.waterfall = Waterfall(self.waterfall_fig, self.waterfall_canvas)
        self.water_ax = self.waterfall.ax
        self._default_plot(self.water_ax)

        # create 1d plot axes in place
        self.int_fig = Figure(tight_layout=True)
        self.int_canvas = FigureCanvas(self.int_fig)
        self.int_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
        self.int_ax = self.int_fig.add_subplot(111)
        self.int_ax.set_autoscale_on(False)
        self._default_plot(self.int_ax)
        # link slider of image viewer with 1d plot
        self.viewer.slider.on_changed(self.update_one_dim_plot)

        # adding qt widgets
        self.img_dock = QtGui.QDockWidget("Dockable", self)
        self.img_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.img_dock.setWindowTitle("2D Image")
        self._configure_dock(self.img_dock, self.img_canvas)

        self.int_dock = QtGui.QDockWidget("Dockable", self)
        self.int_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.int_dock.setWindowTitle("1D Integration")
        self._configure_dock(self.int_dock,self.int_canvas)

        self.waterfall_dock = QtGui.QDockWidget("Dockable", self)
        self.waterfall_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.waterfall_dock.setWindowTitle("Waterfall Plot")
        self._configure_dock(self.waterfall_dock, self.waterfall_canvas)

        # add gui buttons
        self.set_up_menu_bar()
        #self.tools_box = QtGui.QToolBar()
        #self.addToolBar(QtCore.Qt.TopToolBarArea, self.tools_box)
        #self.set_up_tool_bar()

        # These statements add the dock widgets to the GUI
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,
                           self.img_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.int_dock)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,
                           self.waterfall_dock)

    def _configure_dock(self, qt_dock, canvas):
        """helper function to add mpl toolbar"""
        layout = QtGui.QVBoxLayout()
        layout.addWidget(NavigationToolBar(canvas, self))
        layout.addWidget(canvas)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        qt_dock.setWidget(multi)

    def _default_plot(self, ax):
        """method to display only text but not plot
        called when error occurs
        """
        ax.text(.5, .5,
                '{}'.format("xpdView is a part of xpdAcq workflow\n"
                            "therefore it expects data generated"
                            "from standard pipeline.\nPlease go to "
                            "our online documentation for more details:\n"
                            "http://xpdacq.github.io/quickstart.html"),
                     ha='center', va='center', color='w',
                     transform= ax.transAxes, size=12)
        ax.set_facecolor('k')

    def update(self, key_list=None, img_data_list=None,
               int_data_list=None, refresh=False):
        """method to update data carried by class"""
        # key_list is required
        if not key_list:
            print("INFO: can't update without setting key_list")
            return
        # call update methods of each class
        self.viewer.update(key_list, img_data_list, refresh)
        self.waterfall.update(key_list, int_data_list, refresh)
        # re-link callback again
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
            popup = QtGui.QFileDialog()
            self.filepath = popup.getExistingDirectory()
        # list files. xpdAcq logic should be required inexplicitly here
        sorted_fn_list = sorted(os.listdir(self.filepath))
        tif_fn_list = [f for f in sorted_fn_list
                       if os.path.splitext(f)[1] == '.tif']
        chi_fn_list = [f for f in sorted_fn_list
                       if os.path.splitext(f)[1] == '.chi']
        if len(tif_fn_list) != len(chi_fn_list):
            print("number of tif files are not equal to the number of "
                  "chi file")
            return
        key_list = []
        img_data_list = []
        int_data_list = []
        for tif, chi in zip(tif_fn_list, chi_fn_list):
            stem, ext = os.path.splitext(tif)
            key_list.append(stem)
            img_data_list.append(imread(os.path.join(self.filepath,
                                                     tif)))
            # this will block fit2d chi file
            _array = np.loadtxt(os.path.join(self.filepath,chi))
            x = _array[:,0]
            y = _array[:,1]
            int_data_list.append((x, y))
        # filebased operation - always refresh
        self.update(key_list, img_data_list, int_data_list, True)

    def refresh(self):
        """method to reload files in current directory. it's basically a
        set_path method operates on filepath being set currently"""
        self.set_path(refresh=True)

    def update_one_dim_plot(self, val):
        # use the same rounding logic
        _val = int(round(val))
        int_data_list = self.waterfall.int_data_list  # obtain from waterfall
        key_list = self.waterfall.key_list
        _array = int_data_list[_val]
        x,y = _array
        self.int_ax.set_facecolor('w')
        self.int_ax.cla()
        self.int_ax.plot(x,y)
        self.int_ax.set_title(key_list[_val], fontsize=10)
        # FIXME: add x,y label
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
        setpath = QtGui.QAction("&Set Directory", self)
        setpath.setShortcut("Ctrl+O")
        setpath.setStatusTip("Set image directory")
        setpath.triggered.connect(self.set_path)

        # sets up menu refresh option
        refresh_path = QtGui.QAction('&Refresh', self)
        refresh_path.setShortcut('Ctrl+R')
        refresh_path.triggered.connect(self.refresh)

        # This creates the window redocking option in the code
        reset_windows = QtGui.QAction('&Redock Windows', self)
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
        refresh_btn = QtGui.QPushButton('Refresh', self)
        refresh_btn.clicked.connect(self.refresh)
        self.tools_box.addWidget(refresh_btn)

    def reset_window_layout(self):
        """This method puts all of the dock windows containing plots
        back into their original positions
        """
        self.int_dock.setFloating(False)
        self.img_dock.setFloating(False)
        self.waterfall_dock.setFloating(False)

def main():
    """
    This allow the GUI to be run if the program is called as a file

    Returns
    -------
    None

    """
    app = QtGui.QApplication(sys.argv)
    viewer = XpdView()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
