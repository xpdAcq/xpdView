##############################################################################
#
# xpdView.peak_finding      SULI
#                           (c) 2016 Brookhaven Science Associates,
#                           Brookhaven National Laboratory.
#                           All rights reserved.
#
# File coded by:            Caleb Duff
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

"""
This file will hold the code to create the PeakPlot class that will be used by the code to create plots with relation
to the peaks. This class is modeled off of Chris Wright's peak searching code found here:
https://github.com/CJ-Wright/xpd_workflow/blob/integration/xpd_workflow/energy_calib_new.py
"""

import scipy.signal
import numpy as np
import matplotlib.pyplot as plt


class PeakPlot(object):
    """
    This class handles the plotting of peak related parameters

    Attributes
    ----------
    sides : int
        this tells the code how far it should look to the sides of the peak to ensure that a drop off occurred
    order : int
        this tells the code how far to the left and to the right the peak should be the maximum value
    figure : object
        this is the matplotlib figure that the plot should appear on
    canvas : object
        this is the matplotlib canvas that the plot will be drawn on
    int_data : dict
        this is the dictionary containing the integrated data on which the code will search for peaks
    intensity_threshold : int
        this is the threshold intensity, meaning the minimum required intensity to be considered a peak
    keys : list of strings
        list of strings in order that data should be observed in
    frame_numbers : list
        this list simply creates the x data associated with the peak positions
    peak_points : list
        this list contains the peak points corresponding to each image
    ax : object
        the axes that we want the plot to be drawn on
    """

    def __init__(self, figure, canvas, int_data_dict, keys, sides=0, order=30, intensity_threshold=-1):
        """
        This initializes the class
        Parameters
        ----------
        figure : object
            see class attributes
        canvas : object
            see class attributes
        int_data_dict : dict
            see class attributes
        keys : list of strings
            see class attributes
        sides : int
            see class attributes
        order : int
            see class attributes
        intensity_threshold : int
            see class attributes
        """
        self.sides = sides
        self.order = order
        self.fig = figure
        self.canvas = canvas
        self.int_data = int_data_dict
        self.keys = keys
        self.intensity_threshold = intensity_threshold
        self.frame_numbers = []
        self.peak_points = []
        self.ax = self.fig.add_subplot(111)

    def get_peaks(self, x_data, y_data):
        """
        This method finds all of the peaks according to the conditions given
        Parameters
        ----------
        x_data : list of float values
            this list should contain the x values associated with the 1d integrated pattern
        y_data : list of float values
            this list should contain the y values associated with the 1d integrated pattern

        Returns
        -------
        peak_positions : list of float values
            this list will contain all of the peak positions on the x-axis

        """
        # Find all potential peaks
        preliminary_peaks = scipy.signal.argrelmax(y_data, order=self.order)[0]

        if self.sides != 0 and self.intensity_threshold != -1:
            # peaks must have at least sides pixels of data to work with
            preliminary_peaks2 = preliminary_peaks[
                np.where(preliminary_peaks < len(y_data) - self.sides)]

            # make certain that a peak has a drop off which causes the peak
            # height to be more than twice the height at sides
            criteria = y_data[preliminary_peaks2] >= 2 * y_data[preliminary_peaks2 + self.sides]
            criteria *= y_data[preliminary_peaks2] >= 2 * y_data[preliminary_peaks2 - self.sides]
            criteria *= y_data[preliminary_peaks2] >= self.intensity_threshold

            peaks = preliminary_peaks[np.where(criteria)]
            peak_positions = x_data[peaks]

            return peak_positions
        else:
            return x_data[preliminary_peaks]

    def get_plot(self):
        """
        This method simply gets the plot for the user of the peak positions
        Parameters
        ----------
        self

        Returns
        -------
        None

        """
        i = 0
        for key in self.keys:
            peak_points = self.get_peaks(self.int_data[key][0], self.int_data[key][1])
            for peak in peak_points:
                self.frame_numbers.append(i)
                self.peak_points.append(peak)
            i += 1

        self.ax.plot(self.frame_numbers, self.peak_points, 'bo')
        self.ax.set_ylabel("Peak Position in q_A^-1")
        self.ax.hold(False)
        self.ax.autoscale()
        self.canvas.draw()

    def update_the_plot(self, new_keys, new_x, new_y):
        """
        This method will update the plot whenever new data is added in
        Parameters
        ----------
        new_keys : list of strings
            list of strings associated with new data
        new_x : list of 1d arrays
            list of new data to be processed
        new_y : list of 1d arrays
            same as above

        Returns
        -------
        None

        """
        old_length = len(self.keys)
        i = old_length - 1
        j = 0
        for key in new_keys:
            self.keys.append(key)
            peak_points = self.get_peaks(new_x[j], new_y[j])
            for peak in peak_points:
                self.frame_numbers.append(i)
                self.peak_points.append(peak)
            i += 1
            j += 1

        self.ax.cla()
        self.ax.plot(self.frame_numbers, self.peak_points, 'bo')
        self.ax.set_ylabel("Peak Position in q_A^-1")
        self.ax.hold(False)
        self.ax.autoscale()
        self.canvas.draw()
