"""
This will create the class that draws the waterfall plot for the Display window
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class WaterFallMaker:
    """
    This class handles the creation of drawing of the waterfall 3D plots in the XPD view Gui

    Attributes
    ----------
    fig : object
        the matplotlib figure that this class operates on
    canvas : object
        the figure canvas that the class operates on
    data : dictionary
        the dictionary containing all of the 1D integrated data that needs to be stacked side by side
    keys : list of string
        the list of key names in order according to time created and read into the software
    ax : object
        the axes of the matplotlib figure that the 3D projection will be created on
    X : numpy array
        contains all of the X data for the 3D projection of the data
    Y : numpy array
        contains the index number of the files that are read in
    Z : numpy array
        contains all of the Y data for the 1D integrated patterns
    """

    def __init__(self, fig, canvas, int_dict, int_key_list):
        """
        This initializes the WaterfallMaker class

        Parameters
        ----------
        fig : object
            must be a matplotlib figure canvas that will be operated on
        canvas :
            must be a matplotlib canvas that can be operated on
        int_dict : dictionary
            must contain the data to be view in pairs of two lists for the x and y data
        int_key_list :
            must contain the keys of all data that will be observed in the 3D projection

        Returns
        -------
        None

        """
        self.fig = fig
        self.canvas = canvas
        self.data = int_dict
        self.keys = int_key_list
        self.ax = fig.gca(projection='3d')
        self.X = None
        self.Y = None
        self.Z = None

    def get_right_shape(self):
        """
        This class prepares all three numpy arrays to send the data into the 3D projections functions
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        self.X = np.ndarray(shape=((len(self.data[self.keys[0]][0])), len(self.keys)))
        self.Y = np.ndarray(shape=((len(self.data[self.keys[0]][0])), len(self.keys)))
        self.Z = np.ndarray(shape=((len(self.data[self.keys[0]][0])), len(self.keys)))
        self.puts_in_data()

    def puts_in_data(self):
        """
        This class reads all of the data in the class's dictionary into the three numpy arrays
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        for i in range(len(self.keys)):
            for j in range(len(self.data[self.keys[0]][0])):
                self.X[j][i] = self.data[self.keys[i]][0][j]
                self.Y[j][i] = i
                self.Z[j][i] = self.data[self.keys[i]][1][j]

    def get_wire_plot(self):
        """
        This method creats a wire frame plot of the data
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        self.ax.cla()
        self.ax.plot_wireframe(self.X, self.Y, self.Z, rstride=0)
        self.ax.set_ylabel('File Index')
        self.ax.get_xaxis().set_ticks([])
        self.ax.w_zaxis.line.set_lw(0.)
        self.ax.set_zticks([])
        self.ax.hold(False)
        self.ax.autoscale()
        self.canvas.draw()

    def get_surface_plot(self):
        """
        This method creates a 3D contour plot of the data
        Parameters
        ----------
        self

        Returns
        -------

        """
        self.ax.cla()
        self.ax.plot_surface(self.X, self.Y, self.Z, cmap='coolwarm')
        self.ax.set_ylabel('File Index')
        self.ax.get_xaxis().set_ticks([])
        self.ax.w_zaxis.line.set_lw(0.)
        self.ax.set_zticks([])
        self.ax.hold(False)
        self.ax.autoscale()
        self.canvas.draw()
