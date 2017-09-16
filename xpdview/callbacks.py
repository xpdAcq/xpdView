from bluesky.callbacks.broker import BrokerCallbackBase
from .waterfall import Waterfall
import matplotlib.pyplot as plt


class LiveWaterfall(BrokerCallbackBase):
    """
    Stream 1D images in a waterfall viewer.

    Parameters
    ----------
    x_name : str
        field name for x dimension
    y_name: str
        field name for y dimension
    db: databroker.Broker instance
        The Broker to fill the events if events are not filled
    units: tuple of str
        The units for the x and y axes
    """

    def __init__(self, x_name, y_name, db=None, units=None,
                 window_title=None):
        super().__init__((x_name, y_name,), db=db)
        self.db = db
        self.x_name = x_name
        self.y_name = y_name
        self.units = units

        self.fig = plt.figure(window_title)

        self.wf = Waterfall(fig=self.fig, unit=self.units)
        self.i = 0
        self.fig.show()

    def start(self, doc):
        self.i = 0
        self.wf.key_list.clear()
        self.wf.int_data_list.clear()

    def event(self, doc):
        super().event(doc)
        y = doc['data'][self.y_name]
        x = doc['data'][self.x_name]
        self.update((x, y))

    def update(self, data):
        self.wf.update(key_list=[self.i], int_data_list=[data])
        self.i += 1
