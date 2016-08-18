##############################################################################
#
# XPD_view.waterfall_2D        HSRP
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

"""This module handles the 2d waterfall plot
"""
import matplotlib.pyplot as plt
import numpy as np

class Waterfall2D:

    def __init__(self, key_list, data_dict, fig, canvas):
        """The constructor for the Waterfall2D object

        Parameters
        ----------
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
        self.canvas = canvas
        self.ax = self.fig.add_subplot(111)
        self.x_offset = 0
        self.y_offset = 0
        self.normalized_data = dict()

    def generate_waterfall(self):
        self.normalized_data.clear()
        self.normalized_data = self.normalize_data()
        for i in range(0, len(self.key_list)):
            temp_x, temp_y = self.normalized_data[self.key_list[i]]
            temp_x += self.x_offset * i
            temp_y += self.y_offset * i
            self.ax.plot(temp_x, temp_y)
        self.ax.hold(True)
        self.ax.autoscale()
        self.canvas.draw()

    def normalize_data(self):
        temp_dict = dict()
        for key in self.key_list:
            temp = self.data_dict[key]
            temp[1] = temp[1] - temp[1].min()
            temp[1] = temp[1] / (temp[1].max() - temp[1].min())
            temp_dict[key] = temp
        return temp_dict
    



