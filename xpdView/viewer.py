"""
This file will contain the code that makes the XPD view GUI
"""
import sys
import numpy as np
# FIXME: update qt5 if it's fully compatible
from PyQt4 import QtGui, QtCore
import matplotlib
matplotlib.use('Qt4Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolBar

# classes for plotting
from xpdView.cross_2d import CrossSection, StackViewer
from xpdView.waterfall import Waterfall

class XpdView(QtGui.QMainWindow):
    def __init__(self, key_list=None, img_data_list=None,
                 int_data_list=None):
        """
        a class holds 2d/1d data and it's corresponding names

        Attributes
        ----------
        key_list : list
            list of data keys
        img_data_list : list
            a list of images carried by this class
        int_data_list : list
            a list 1d reduced data carried by this class
        """
        # configure QT property
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle('XPD View')
        self.setDockNestingEnabled(True)
        self.setAnimated(False)

        # set lists of data carried by class
        self.key_list = key_list
        self.img_data_list = img_data_list
        self.int_data_list = int_data_list

        # init mpl figures and canvas for plotting
        self.img_fig = plt.figure()
        self.img_canvas = FigureCanvas(self.img_fig)
        self.img_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)
        self._viewer = CrossSection(self.img_fig) # core 2d viewer
        self.viewer = StackViewer(self._viewer) # stack viwer

        self.waterfall_fig = plt.figure()
        self.waterfall_canvas = FigureCanvas(self.waterfall_fig)
        self.waterfall_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                            QtGui.QSizePolicy.Expanding)
        self.waterfall = Waterfall(self.waterfall_fig, self.waterfall_canvas)
        self.water_ax = self.waterfall.ax

        self.int_fig = plt.figure()
        self.int_canvas = FigureCanvas(self.int_fig)
        self.int_canvas.setSizePolicy(QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Expanding)

        # adding qt widgets
        self.img_dock = QtGui.QDockWidget("Dockable", self)
        self.img_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.img_dock.setWindowTitle("2D Image")
        self._configure_dock(self.img_dock, self.img_canvas)

        self.int_dock = QtGui.QDockWidget("Dockable", self)
        self.int_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.int_dock.setWindowTitle("1D Integration")
        #self._configure_dock(self.int_dock,self.int_canvas)

        self.waterfall_dock = QtGui.QDockWidget("Dockable", self)
        self.waterfall_dock.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        self.waterfall_dock.setWindowTitle("Waterfall Plot")
        self._configure_dock(self.waterfall_dock, self.waterfall_canvas)

        self.tools_box = QtGui.QToolBar()
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.tools_box)
        self.set_up_menu_bar()
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
        layout = QtGui.QVBoxLayout()
        layout.addWidget(NavigationToolBar(canvas, self))
        layout.addWidget(canvas)
        multi = QtGui.QWidget()
        multi.setLayout(layout)
        qt_dock.setWidget(multi)
        canvas.figure.tight_layout()

    def update(self, key_list=None, img_data_list=None,
               int_data_list=None, refresh=False):
        """method to update data carried by class"""
        # key_list is required
        if not key_list:
            print("I can't update")
            return
        # update method of each class
        self.viewer.update(key_list, img_data_list, refresh)
        #self.waterfall.update(key_list, int_data_list,


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


    def configure_waterfall(self):
        """
        This handles plotting the 2d waterfall
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        # configure gui layout
        mpl_toolbar = NavigationToolBar(self.water_canvas, self)
        layout = QtGui.QVBoxLayout()
        grid = QtGui.QGridLayout()
        grid.addWidget(mpl_toolbar, 0, 0)
        layout.setSizeConstraint(QtGui.QLayout.SetMinimumSize)
        layout.addLayout(grid)
        layout.addWidget(self.water_canvas)
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
        window_menu = mainmenu.addMenu("&Window")
        filemenu.addAction(setpath)
        filemenu.addAction(refresh_path)
        window_menu.addAction(reset_windows)

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
        # All these commands will add the widgets in
        refresh_btn = QtGui.QPushButton('Refresh', self)
        refresh_btn.clicked.connect(self.refresh)
        self.tools_box.addWidget(refresh_btn)

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
        self.waterfall_dock.setFloating(False)

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
        #FIXME: load method


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
