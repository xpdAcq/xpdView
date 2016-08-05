"""
This will create the class that draws the waterfall plot for the Display window
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class WaterFallMaker:
    def __init__(self, fig, canvas, int_dict, int_key_list):
        self.fig = fig
        self.canvas = canvas
        self.data = int_dict
        self.keys = int_key_list
        self.ax = fig.gca(projection='3d')
        self.X = None
        self.Y = None
        self.Z = None

    def get_right_shape(self):
        self.X = np.ndarray(shape=((len(self.data[self.keys[0]][0])), len(self.keys)))
        self.Y = np.ndarray(shape=((len(self.data[self.keys[0]][0])), len(self.keys)))
        self.Z = np.ndarray(shape=((len(self.data[self.keys[0]][0])), len(self.keys)))
        self.puts_in_data()

    def puts_in_data(self):
        for i in range(len(self.keys)):
            for j in range(len(self.data[self.keys[0]][0])):
                self.X[j][i] = self.data[self.keys[i]][0][j]
                self.Y[j][i] = i
                self.Z[j][i] = self.data[self.keys[i]][1][j]

    def get_wire_plot(self):
        self.ax.cla()
        self.ax.plot_wireframe(self.X, self.Y, self.Z, rstride=0)
        self.ax.set_ylabel('File Index')
        self.ax.get_xaxis().set_ticks([])
        self.ax.w_zaxis.line.set_lw(0.)
        self.ax.set_zticks([])
        self.ax.hold(False)
        self.ax.autoscale()
        self.canvas.draw()

    def get_surface_plot(self):
        self.ax.plot_surface(self.X, self.Y, self.Z, cmap='coolwarm')
        self.ax.set_ylabel('File Index')
        self.ax.get_xaxis().set_ticks([])
        self.ax.w_zaxis.line.set_lw(0.)
        self.ax.set_zticks([])
        self.ax.hold(False)
        self.ax.autoscale()
        self.canvas.draw()
