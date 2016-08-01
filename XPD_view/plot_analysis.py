import matplotlib.pyplot as plt
import numpy as np
import multiprocessing


class ReducedRepPlot:

    def __init__(self, data_dict, key_list, x_start, x_stop, y_start, y_stop, selection, figure, canvas):
        """
        constructor for reducedRepPlot object
        :param file_path: path to file directory
        :type file_path: str
        :param x_start: start val for x analysis
        :param x_stop: stop val for x analysis
        :param y_start:
        :param y_stop:
        """

        # self.tif_list = get_files(file_path)
        assert x_start >= 0 and x_start < x_stop
        assert x_stop <= 2048 #TODO change so resolution is flexible
        assert y_start >= 0 and y_start < y_stop
        assert y_stop <= 2048 #TODO change so resolution is flexible

        self.data_dict = data_dict
        self.key_list = key_list
        self.x_start = x_start
        self.x_stop = x_stop
        self.y_start = y_start
        self.y_stop = y_stop
        self.selection = selection
        self.y_data = None
        self.is_Plotted = False
        self.ax = None
        self.fig = figure
        self.canvas = canvas
        # default func dict is simple analysis functions
        self.func_dict = {np.std.__name__: np.std, np.mean.__name__: np.mean, np.amin.__name__: np.amin,
                          np.amax.__name__: np.amax, np.sum.__name__: np.sum}

    def analyze(self):
        """
        This function will plot analysis data as a function of the number of images. uses multiprocessing to speed
        things up
        :return: void
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
        """
        an overloaded analyze method that will take in a data list and return an analyzed list
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

        if new_data is None:
            self.fig.canvas.mpl_connect('close_event', self.handle_close)
            self.ax = self.fig.add_subplot(111)
            self.ax.plot(range(0, len(self.y_data)), self.y_data, 'ro')
            self.ax.set_xlabel("File Num")
            self.ax.set_ylabel(self.selection)
            self.ax.hold(False)
            self.ax.autoscale()
            self.is_Plotted = True
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

    def handle_close(self, event):
        self.is_Plotted = False

    def set_func_dict(self, func_list):
        """a setter for func_dict that takes in a list of functions 
        and creates a dictionary for them
        functions should have the arguments
        arr for the 2d image array
        """
        self.func_dict.clear()
        for func in func_list:
            self.func_dict[func.__name__] = func

    def add_func(self, func):
        """functions should have the arguments
        arr for the 2d image array
        """
        self.func_dict[func.__name__] = func

