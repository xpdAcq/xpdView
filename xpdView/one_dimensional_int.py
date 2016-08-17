##############################################################################
#
# xpdView.one_dimensional_int       SULI
#                                   (c) 2016 Brookhaven Science Associates,
#                                   Brookhaven National Laboratory.
#                                   All rights reserved.
#
# File coded by:                    Caleb Duff
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
This file will handle all of the one dimensional plotting of the lower left tile in the
Display Window
"""

import matplotlib.pyplot as plt


class IntegrationPlot(object):
    """
    This class handles the drawing of the integrated data plots

    Attributes
    ----------
    int_data_dict : dict
        this dictionary holds the data to be plotted by the user; data must be stored as lists inside a list with the
        format [x_data_list, y_data_list]
    fig : object
        this needs to be a matplotlib figure
    canvas : object
        the canvas associated in the above figure
    ax : object
        a subplot on the figure
    """

    def __init__(self, dictionary, fig, canvas):
        """
        This initializes the IntegrationPlot class

        Parameters
        ----------
        dictionary: dictionary
            contains pairs of lists [[list_x], [list_y]] from the 1D integrated data
        fig: object
            matplotlib figure to be operated on
        canvas: object
            the canvas associated with the above figure

        Returns
        -------
        None
        """
        self.int_data_dict = dictionary
        self.fig = fig
        self.canvas = canvas
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Distance from Center')
        self.ax.set_ylabel('Total Integrated Intensity')
        self.ax.set_title('1-D Integrated Plot')
        self.give_plot('nothing')

    def give_plot(self, key):
        """
        This method draws the desired 1D integrated plot
        Parameters
        ----------
        key : str
            key of integrated data to be viewed

        Returns
        -------
        None

        """
        if key[-4:] == '.tif':
            use_key = key[:-4] + '.chi'
        else:
            use_key = key

        try:
            data = self.int_data_dict[use_key]
            self.ax.plot(data[0], data[1])
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()
        except KeyError:
            self.ax.plot([], [])
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()
        except IndexError:
            self.ax.plot([], [])
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()
