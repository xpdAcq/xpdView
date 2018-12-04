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
                 key_list=None, int_data_list=None,
                 *, unit=None, **kwargs):
        if int_data_list is None:
            int_data_list = []
        if key_list is None:
            key_list = []
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
        self.key_list = key_list
        self.int_data_list = int_data_list
        self.ax = self.fig.add_subplot(111)
        self.unit = unit
        self.halt = False
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
        # init
        self.update(self.key_list, self.int_data_list, refresh=True)

    def update(self, key_list=None, int_data_list=None, refresh=False):
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
        if not int_data_list:
            print("INFO: no reduced data was fed in, "
                  "waterfall plot can't be updated")
            self.halt = True
            return
        # refresh list
        if refresh:
            self.key_list = []
            self.int_data_list = []
        self.key_list.extend(key_list)
        self.int_data_list.extend(int_data_list)
        self._adapt_data_list(self.int_data_list)
        # generate plot
        self.halt = False
        self._update_plot()  # use current value of x,y offset

    def _adapt_data_list(self, int_data_list):
        """method to return statefull information of 1D data list"""
        # parse
        x_dist, y_dist = 0, 0
        for x, y in int_data_list:
            self.xdist = max(np.ptp(x), self.xdist)
            self.ydist = max(np.ptp(y), self.ydist)
            self.x_array_list.append(x)
            self.y_array_list.append(y)
        self.x_dist = x_dist
        self.y_dist = y_dist

    def on_plot_hover(self, event):
        """callback to show legend when click on one of curves"""
        line = event.artist
        name = line.get_label()
        line.axes.legend([name], handlelength=0,
                         handletextpad=0, fancybox=True)
        line.figure.canvas.draw_idle()

    def _update_plot(self, x_offset_val=None, y_offset_val=None):
        """core method to update x-, y-offset sliders"""
        # remain current offset
        if not x_offset_val:
            x_offset_val = self.x_offset_slider.val
        if not y_offset_val:
            y_offset_val = self.y_offset_slider.val
        # draw if fresh axes
        if not self.ax.get_lines():
            for ind, el in enumerate(zip(self.x_array_list,
                                         self.y_array_list,
                                         self.key_list)):
                x, y, k = el
                self.ax.plot(x, y, label=k, picker=5,
                             **self.kwargs)
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
        if self.halt:
            return
        self._update_plot(None, val)

    def update_x_offset(self, val):
        if self.halt:
            return
        self._update_plot(val, None)
