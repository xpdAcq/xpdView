import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from cycler import cycler

simonCycle2 = ["#0B3C5D", "#B82601", "#1c6b0a",
               "#328CC1", "#062F4F", "#D9B310",
               "#984B43", "#76323F", "#626E60",
               "#AB987A", "#C09F80", "#b0b0b0ff"]
mpl.rcParams['axes.prop_cycle'] = cycler(color=simonCycle2)

plt.rcParams['axes.linewidth'] = 3.0
plt.rcParams['figure.dpi'] = 100
plt.rcParams['lines.linewidth'] = 2.0
plt.rcParams['font.size'] = 14


class Waterfall:
    """class holds data and generate watefall plot

    Parameters
    ----------
    fig : matplotlib.Figure
        fig this waterfall plot will be drawn on
    canvas : matplotlib.Canvas
        canvas this waterfall plot will be drawn on
    key_list : list, optional
        list of key names. default to None
    int_data_list : list, optional
        list of 1D reduced data. expect each element to be in (x,y)
        format. default to None
    unit : tuple, optional
        a tuple containing strings of x and y labels
    kwargs :
        keyword arguments for plotting
    """

    def __init__(self, fig=None, canvas=None,
                 *, unit=None, **kwargs):
        if not fig:
            fig = plt.figure()

        self.fig = fig

        if not canvas:
            canvas = self.fig.canvas
        self.canvas = canvas
        self.kwargs = kwargs
        self.x_array_list = []
        self.y_array_list = []

        # callback for showing legend
        self.canvas.mpl_connect('pick_event', self.on_plot_hover)
        self.key_list = []
        self.int_data_list = []
        self.ax = self.fig.add_subplot(111)
        self.unit = unit

        # add sliders, which store information
        self.ydist = 0
        self.xdist = 0

        y_offset_slider_ax = self.fig.add_axes([0.15, 0.95, 0.3, 0.035])
        self.y_offset_slider = Slider(y_offset_slider_ax,
                                      'y-offset', 0.0, 1.0,
                                      valinit=0.1, valfmt='%1.2f')
        self.y_offset_slider.on_changed(self.update_y_offset)

        x_offset_slider_ax = self.fig.add_axes([0.6, 0.95, 0.3, 0.035])
        self.x_offset_slider = Slider(x_offset_slider_ax,
                                      'x-offset', 0.0, 1.0,
                                      valinit=0., valfmt='%1.2f')
        self.x_offset_slider.on_changed(self.update_x_offset)

    def update(self, key_list, int_data_list):
        """top method to update information carried by class and plot

        Parameters
        ----------
        key_list : list, optional
            list of keys. default to None.
        int_data_list : list, optional
            list of 1D data. default to None.
        refresh : bool, optional
            option to set refresh or not. default to False.
        """
        self.key_list.extend(key_list)
        self.int_data_list.extend(int_data_list)
        # generate plot
        self._update_data()
        self._update_plot()  # use current value of x,y offset

    def _adapt_data_list(self, int_data_list):
        """method to return stateful information of 1D data list"""
        # parse
        x_dist, y_dist = 0, 0
        for x, y in int_data_list:
            self.xdist = max(np.ptp(x), self.xdist)
            self.ydist = max(np.ptp(y), self.ydist)
            self.x_array_list.append(x)
            self.y_array_list.append(y)
        self.x_dist = x_dist
        self.y_dist = y_dist

    def _update_data(self):
        # draw if fresh axes
        if not self.ax.get_lines():
            for ind, el in enumerate(zip(self.x_array_list,
                                         self.y_array_list,
                                         self.key_list)):
                x, y, k = el
                self.ax.plot(x, y, label=k, picker=5,
                             **self.kwargs)
        if len(self.ax.get_lines()) < len(self.int_data_list):
            diff = len(self.int_data_list) - len(self.ax.get_lines())
            for ind, el in enumerate(zip(self.x_array_list[-diff:],
                                         self.y_array_list[-diff:],
                                         self.key_list[-diff:])):
                x, y, k = el
                self.ax.plot(x, y, label=k, picker=5,
                             **self.kwargs)

    def _update_plot(self):
        """core method to update x-, y-offset sliders"""
        self._adapt_data_list(self.int_data_list)

        x_offset_val = self.x_offset_slider.val
        y_offset_val = self.y_offset_slider.val
        # update matplotlib line data
        lines = self.ax.get_lines()
        for i, (l, x, y) in enumerate(zip(lines,
                                          self.x_array_list,
                                          self.y_array_list)):
            xx = x+self.xdist*i*x_offset_val
            yy = y+self.ydist*i*y_offset_val
            l.set_data(xx, yy)
        self.ax.relim()
        self.ax.autoscale_view()
        if self.unit:
            xlabel, ylabel = self.unit
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
        self.canvas.draw_idle()

    def update_y_offset(self, val):
        self._update_plot()

    def update_x_offset(self, val):
        self._update_plot()

    def on_plot_hover(self, event):
        """callback to show legend when click on one of curves"""
        line = event.artist
        name = line.get_label()
        line.axes.legend([name], handlelength=0,
                         handletextpad=0, fancybox=True)
        line.figure.canvas.draw_idle()

    def clear(self):
        self.key_list.clear()
        self.int_data_list.clear()
        self.ax.lines.clear()
        self.canvas.draw_idle()
