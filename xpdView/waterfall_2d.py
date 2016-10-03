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


class Waterfall2D:

    def __init__(self, key_list, data_dict, fig, canvas):
        """The constructor for the Waterfall2D object

        Parameters
        ----------
        key_list : list
            the ordered list that contains the keys for the integrated data
        data_dict : dict
            the dictionary that contains the data for plotting
        fig : matplotlib figure
            the figure object for the plot
        canvas : qt canvas
            the canvas that will be drawn on
        """
        self.data_dict = data_dict
        self.key_list = key_list
        self.fig = fig
        self.normalized = False
        self.canvas = canvas
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
        title = 'Data not normalized'
        if self.normalized:
            data = self.normalized_data
            title = 'Data Normalized'
        else:
            data = self.data_dict
        list_data = (data[k] for k in self.key_list)  # you can do a list comp here too
        for i, (x, y) in enumerate(list_data):
            self.ax.plot(x + self.x_offset * i, y + self.y_offset * i)
        self.ax.set_title(title)
        self.ax.autoscale()
        self.canvas.draw()

    def is_normalized(self):
        return self.normalized

    def set_normalized(self, state):
        self.normalized = state

    def normalize_data(self):
        """This method normalizes data for plotting

        Returns
        -------
        None
        """
        self.normalized_data.clear()
        for key in self.key_list:
            temp = self.data_dict[key].copy()
            temp[1] = temp[1] - temp[1].min()
            temp[1] = temp[1] / (temp[1].max() - temp[1].min())
            self.normalized_data[key] = temp
