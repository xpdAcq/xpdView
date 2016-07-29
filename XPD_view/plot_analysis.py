import matplotlib.pyplot as plt
from analysis_concurrent import analysis_concurrent
import time
import multiprocessing


class reducedRepPlot:

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


    def analyze(self):
        """
        This function will plot analysis data as a function of the number of images. uses multiprocessing to speed
        things up
        :return: void
        """
        a = analysis_concurrent(self.y_start, self.y_stop, self.x_start, self.x_stop, self.selection)
        p = multiprocessing.Pool()
        values = []
        for key in self.key_list:
            values.append(self.data_dict[key])
        
        y = p.map(a.x_and_y_vals, values)
        p.close()
        p.join()
        
        print(y)

        assert (len(y) == len(self.key_list))
        self.y_data = y

    def analyze_new_data(self, data_list):
        """
        an overloaded analyze method that will take in a data list and return an analyzed list
        """
        a = analysis_concurrent(self.y_start, self.y_stop, self.x_start, self.x_stop, self.selection)
        p = multiprocessing.Pool()
        y = p.map(a.x_and_y_vals, data_list)
        p.close()
        p.join()
        
        print(y)

        return y


    def show(self, new_data = None):

        if new_data is None:
            self.fig.canvas.mpl_connect('close_event', self.handle_close)
            self.ax = self.fig.add_subplot(111)
            self.ax.plot(range(0, len(self.y_data)), self.y_data, 'ro')
            self.ax.set_xlabel("File Num")
            self.ax.set_ylabel(self.selection)
            self.ax.hold(False)
            # plt.plot(range(0, len(self.y_data)), self.y_data, 'ro')
            # plt.xlabel("file num")
            # plt.ylabel(self.selection)

            #  plt.xscale()
            #
            self.is_Plotted = True
            # plt.ion()
            # plt.draw()
            # plt.show()
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

    # def redraw(self, new_data):
    #
    #     if not self.is_Plotted:
    #         self.show()
    #     else:
    #         new_data = self.analyze_new_data(new_data)
    #         for val in new_data:
    #             self.y_data.append(val)
    #         self.axes.set_xdata(range(0, len(self.y_data)))
    #         self.axes.set_ydata(self.y_data)
    #         self.axes.draw()


    def handle_close(self, event):
        self.is_Plotted = False
        print("closed")


