##############################################################################
#
# xpdView.waterfall_2D         HSRP
#                              (c) 2016 Brookhaven Science Associates,
#                              Brookhaven National Laboratory.
#                              All rights reserved.
#
# File coded by:               Joseph Kaming-Thanassi
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
This module handles the 2d waterfall plot
"""
import numpy as np

class Waterfall2D:

    def __init__(self, key_list, data_dict, fig, canvas):
        """The constructor for the Waterfall2D object

        Parameters
        ----------
        key_list : list
            list contains the keys for the integrated data
        data_dict : dict
            dict contains the data for plotting
        fig : matplotlib figure
            the figure object for the plot
        canvas : qt canvas
            the canvas that will be drawn on
        """
        self.data_dict = data_dict
        self.key_list = key_list
        self.fig = fig
        self.normalized = True
        self.canvas = canvas
        # clean
        self.fig.clf()
        self.ax = self.fig.add_subplot(111)
        self.x_offset = 0
        self.y_offset = 0
        self.normalized_data = dict()

    def generate_waterfall(self):
        """This method handles the plotting of the 2d waterfall

        Returns
        -------
        None
        """
        self.ax.cla()
        if self.normalized and self.data_dict:
            self.normalize_data()
            data = self.normalized_data
        else:
            data = self.data_dict
        list_data = list(data.values())  # you can do a list comp here too
        for i, meta in enumerate(list_data):
            x,y = meta
            self.ax.plot(x + self.x_offset * i, y + self.y_offset * i)
        #self.ax.set_title(title)
        short_key_list = list(map(lambda x: x[:10], self.key_list))
        self.ax.legend(short_key_list)
        self.ax.set_xlabel('a.u.')
        self.ax.autoscale()
        self.canvas.draw()

    # TODO: turn into property
    def is_normalized(self):
        return self.normalized

    def set_normalized(self, state):
        self.normalized = state

    def normalize_data(self):
        """normalize data grid and intensity"""
        # copy dict
        self.normalized_data = dict(self.data_dict)
        # find the finest grid
        grid_list= [x for x, y in self.data_dict.values()]
        grid = sorted(grid_list, key=lambda x: x.shape).pop()  # finest grid
        for k, val in self.data_dict.items():
            x,y = val
            #_y = np.interp(grid, x, y)  # don't interp, blow if necessary
            _y = (y-np.min(y))/(np.max(y)-np.min(y))
            self.normalized_data[k] = (x, _y)