import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

def _normalize(self, array, max_val, min_val):
    """core function to normalize a ndarray"""
    return np.subtract(array, min_val) / np.subtract(max_val, min_val)

# needed by init
#canvas = FigureCanvas(fig)
#water_fig = plt.figure()
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
    """
    def __init__(self, fig, canvas, key_list=None, int_data_list=None):
        self.fig = fig
        self.canvas = canvas
        self.key_list = key_list
        self.int_data_list = int_data_list
        self.ax = self.fig.add_subplot(111)
        # add sliders, which store informations
        y_offset_slider_ax = self.fig.add_axes([0.1, 0.97, 0.3, 0.02])
        self.y_offset_slider = Slider(y_offset_slider_ax,
                                      'y-offset', 0.0, 1.0,
                                      valinit=0.1, valfmt='%1.2f')
        self.y_offset_slider.on_changed(self.update_y_offset)

        x_offset_slider_ax = self.fig.add_axes([0.6, 0.97, 0.3, 0.02])
        self.x_offset_slider = Slider(x_offset_slider_ax,
                                      'x-offset', 0.0, 1.0,
                                      valinit=0.1, valfmt='%1.2f')
        self.x_offset_slider.on_changed(self.update_x_offset)
        # init
        self.update(self.key_list, self.int_data_list, refresh=True)
        self.default_plot()

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
        # update/refresh list
        if refresh:
            self.key_list = key_list
            self.int_data_list = int_data_list
        else:
            self.key_list.extend(key_list)
            self.int_data_list.extend(int_data_lit)
        # generate plot
        if self.int_data_list:
            self._update_plot()# use current value
        else:
            return

    def _adapt_data_list(self, int_data_list):
        """method to return statefull information of 1D data list"""
        x_array_list = []
        y_array_list = []
        for x,y in int_data_list:
            x_array_list.append(x)
            y_array_list.append(y)
        y_max = np.max(y_array_list)
        y_min = np.min(y_array_list)
        y_dist = y_max - y_min
        x_max = np.max(x_array_list)
        x_min = np.min(x_array_list)
        x_dist = x_max - x_min
        return (x_array_list, y_array_list, y_min, y_max,
                y_dist, x_min, x_max, x_dist)

    def _update_plot(self, x_offset_val=None, y_offset_val=None):
        """core method to update x-, y-offset sliders"""
        if not x_offset_val:
            x_offset_val = self.x_offset_slider.val
        if not y_offset_val:
            y_offset_val = self.y_offset_slider.val
        # get stateful info
        state = self._adapt_data_list(self.int_data_list)
        x_array_list, y_array_list,\
                y_min, y_max, y_dist, x_min, x_max, x_dist = state
        for ind, el in enumerate(zip(x_array_list, y_array_list)):
            x, y = el
            self.ax.plot(x + x_dist * ind * x_offset_val,
                               y + y_dist * ind * y_offset_val)
        self.ax.autoscale()
        self.canvas.draw_idle()

    def update_y_offset(self, val):
        self.ax.cla()
        self._update_plot(None, val)

    def update_x_offset(self, val):
        self.ax.cla()
        self._update_plot(val, None)

    def default_plot(self):
        """method to display only text but not plot
        called when error occurs
        """
        #self.ax.text(0.3, 0.5, 'We expect standard xpdAcq data')
        #FIXME: words to display xpdAcq instruction
        pass
