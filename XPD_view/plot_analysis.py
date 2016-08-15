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

        x_start : int
            The starting value for x array slicing defined by the ROI

        x_stop : int
            The stopping value for x array slicing defined by the ROI

        y_start : int
            The starting value for y array slicing defined by the ROI

        y_stop : int
            The stopping value for y array slicing defined by the ROI

        selection : str
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
        """This function will plot analysis data as a function of the number of images.

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

    def set_func_dict(self, func_list):
        """a setter for func_dict that takes in a list of functions

        creates a dictionary for them
        functions should have the arguments
        arr for the 2d image array

        Parameters
        ----------
        func_list : a list of functions that you want to replace the current dictionary functions
        """
        self.func_dict.clear()
        for func in func_list:
            self.func_dict[func.__name__] = func

    def add_func(self, func):
        """adds an arbitrary function to the function dictionary

        the function should have the argument arr for a 2d image array

        Parameters
        ----------
        func : function
            the function to be passed in
        """
        self.func_dict[func.__name__] = func

    def remove_func(self, func_name):
            """This function will remove a function from the function dictionary

            To delete the name of the function must match the name of a function currently in the dictionary

            Parameters
            ----------

            func_name : str
                the name of the function to be removed. best to use func.__name__

            """

            try:
                self.func_dict.__delitem__(func_name)
            except KeyError:
                print("There is no function matching " + func_name + " in the function dictionary")

