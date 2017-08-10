from bluesky.callbacks.broker import BrokerCallbackBase
from .waterfall import Waterfall
import matplotlib.pyplot as plt


class LiveWaterfall(BrokerCallbackBase):
    """
    Stream 2D images in a cross-section viewer.

    Parameters
    ----------
    field : string
        name of data field in an Event
    """

    def __init__(self, field, fs=None):
        import matplotlib.pyplot as plt
        super().__init__((field, ), fs=fs)
        self.field = field
        self.fig = plt.figure()
        self.wf = Waterfall(fig=self.fig)
        self.fs = fs
        self.i = 0

    def event(self, doc):
        super().event(doc)
        data = doc['data'][self.field]
        self.update(data)

    def update(self, data):
        self.wf.update(key_list=[self.i], int_data_list=[data])
        self.i += 1
