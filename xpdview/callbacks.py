import matplotlib.pyplot as plt
from bluesky.callbacks.core import CallbackBase

from .waterfall import Waterfall


class LiveWaterfall(CallbackBase):
    """
    Stream 1D images in a waterfall viewer.

    Parameters
    ----------
    x_name : str
        field name for x dimension
    y_name: str
        field name for y dimension
    units: tuple of str
        The units for the x and y axes
    """

    def __init__(self, x_name, y_name, units=None,
                 window_title=None):
        super().__init__()
        self.x_name = x_name
        self.y_name = y_name
        self.units = units

        self.fig = plt.figure(window_title)
        self.wf = Waterfall(fig=self.fig, unit=self.units)

        self.i = 0

    def start(self, doc):
        self.fig.show()
        self.wf.clear()
        self.i = 0

    def event(self, doc):
        super().event(doc)
        y = doc['data'].get(self.y_name, None)
        x = doc['data'].get(self.x_name, None)
        if x is not None and y is not None:
            self.update((x, y))

    def update(self, data):
        self.wf.update(key_list=[self.i], int_data_list=[data])
        self.i += 1
