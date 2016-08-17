##############################################################################
#
# xpdView.plot_analysis     HSRP
#                   (c) 2016 Brookhaven Science Associates,
#                   Brookhaven National Laboratory.
#                   All rights reserved.
#
# File coded by:    Joseph Kaming-Thanassi
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""This class handles the plotting and analysis for reduced representation
"""

import multiprocessing


class ReducedRepPlot:

    def __init__(self, data_dict, key_list, figure, canvas, func_dict, selection=None):
        """constructor for reducedRepPlot object

        Parameters
        ----------

        data_dict : dict
            The dictionary where the image arrays are stored

        key_list : list
            A list where the keys for the data_dict are kept in order

        selection : str (optional)
            The name of the current function selected for analysis

        figure : matplotlib.figure
            The figure where the reduced rep plotting is drawn

        canvas : FigureCanvas
            The canvas where the reduced rep plotting is drawn


        """

        self.data_dict = data_dict
        self.key_list = key_list
        self.x_start = None
        self.x_stop = None
        self.y_start = None
        self.y_stop = None
        self.selection = selection
        self.y_data = None
        self.ax = None
        self.fig = figure
        self.canvas = canvas
        self.func_dict = func_dict
        # default func dict is simple analysis functions

    def analyze(self):
        """this method handles the concurrent analysis of data
        Returns
        -------
        None

        """
        p = multiprocessing.Pool()
        vals = []
        for key in self.key_list:
            vals.append(self.data_dict[key][self.y_start: self.y_stop, self.x_start: self.x_stop])
        y = p.map(self.func_dict[self.selection], vals)
        p.close()
        p.join()

        assert (len(y) == len(self.key_list))
        self.y_data = y

    def analyze_new_data(self, data_list):
        """an analyze method that will take in a data list and return an analyzed list

        Parameters
        ----------
        data_list : list
            the list of sliced numpy arrays to be analyzed

        Returns
        -------
        a list of y data from the analysis
        """

        p = multiprocessing.Pool()
        vals = []
        for data in data_list:
            vals.append(data[self.y_start: self.y_stop, self.x_start: self.x_stop])
        y = p.map(self.func_dict[self.selection], vals)
        p.close()
        p.join()

        return y

    def show(self, new_data=None):
        """handles plotting for the reduced rep plot panel

        Parameters
        ----------
        new_data : list (optional)
            if the new data list is present, the plot will be updated with new data and not completely redrawn

        Returns
        -------
        None
        """

        if new_data is None:
            self.analyze()
            self.ax = self.fig.add_subplot(111)
            self.ax.plot(range(0, len(self.y_data)), self.y_data, 'ro')
            self.ax.set_xlabel("File Num")
            self.ax.set_ylabel(self.selection)
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()
        else:
            new_data = self.analyze_new_data(new_data)
            for val in new_data:
                self.y_data.append(val)
            self.ax.plot(range(0, len(self.y_data)), self.y_data, 'ro')
            self.ax.set_xlabel("File Num")
            self.ax.set_ylabel(self.selection)
            self.ax.autoscale()
            self.canvas.draw()
