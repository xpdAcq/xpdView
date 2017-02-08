"""module to generate 1d plot"""

class OneDPlot:
    """
    class to hold a list of data key and a list of 1d arrays

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        matplotlib Figure instance
    canvas :
        a qt backend matplotlib canvas
    key_list : list, optional
        list of data keys. default to None.
    int_data_list : list
        list of 1D arrays. default to None.
    """
    def __init__(self, fig, canvas, key_list=None, int_data_list=None):
        # data attributes
        self.fig = fig
        self.canvas = canvas
        self.key_list = key_list
        self.int_data_list = int_data_list
        # adding axes
        self.ax = self.fig.add_subplot(111)

    def update(self, key_list, int_data_list, refresh=False):
        """method to update data carried by class"""
        if refresh:
            self.key_list = key_list
            self.int_data_list = int_data_list
        else:
            self.key_list.update(key_list)
            self.int_data_list.update(int_data_list)
        # doesn't need to redraw, let slider handle

    def update_by_slider(self, val):
        """redraw canvas based on slider value

        Note: this slider presumably lives in other classes
        """
        print("CALLED ond slider update")
        # use the same rounding logic as slider
        if not isinstance(val, int):
            _val = int(round(val))
        _array = self.int_data_list[_val]
        x, y = _array
        self.ax.plot(x, y)
        # FIXME: add x,y label
        self.canvas.draw_idle()
