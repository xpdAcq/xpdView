"""
This file will contain the class that will be used in the plotting of the 2D data in the Display class
for XPD view
"""

import matplotlib.pyplot as plt


class DiffractionData(object):

    def __init__(self, fig, canvas, data_dict):
        self.fig = fig
        self.canvas = canvas
        self.data_dict = data_dict
        self.ax = self.fig.add_subplot(111)

    def draw_image(self, key):
        try:
            self.ax.imshow(self.data_dict[key], origin='lower')
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()
        except KeyError:
            pass
