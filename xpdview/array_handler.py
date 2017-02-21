import warnings
import numpy as np


class ArrayHandler:

    """
    Simple class to carry list of ndarray as a dict form

    Parameters
    ----------
    array_dict : dict
        a array with key as some unique name and value as ndarray
    """
    def __init__(self, array_dict=None, fig=None, canvas=None):
        self._array_dict = array_dict
        self.fig = fig
        self.canvas = canvas
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel('q_A^-1')
        self.ax.set_ylabel('Total Integrated Intensity')
        self.give_plot('nothing')

    def give_plot(self, key):
        """
        This method draws the desired 1D integrated plot
        Parameters
        ----------
        key : str
            key of integrated data to be viewed

        Returns
        -------
        None

        """
        try:
            data = self._array_dict[key]
            self.ax.plot(data[0], data[1])
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()
        except (KeyError, IndexError):
            warnings.warn("invalid data array", UserWarning)
            self.ax.plot([], [])
            self.ax.hold(False)
            self.ax.autoscale()
            self.canvas.draw()

    @property
    def array_dict(self):
        return self._array_dict

    def update_array_dict(self, key, val):
        if isinstance(key, str) and isinstance(val, np.ndarray):
            self._array_dict.update(key, val)
        else:
            print("illegal array_dict")
