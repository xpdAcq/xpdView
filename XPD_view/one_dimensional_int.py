"""
This file will handle all of the one dimensional plotting of the lower left tile in the
Display Window
"""

import matplotlib.pyplot as plt


class IntegrationPlot(object):

    def __init__(self, dictionary, keys, fig, canvas, index=0):
        self.int_data_dict = dictionary
        self.key_list = keys
        self.fig = fig
        self.canvas = canvas
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('Distance from Center')
        self.ax.set_ylabel('Total Integrated Intensity')
        self.ax.set_title('1-D Integrated Plot')
        self.give_plot(index)

    def give_plot(self, index):
        try:
            data = self.int_data_dict[self.key_list[index]]
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
