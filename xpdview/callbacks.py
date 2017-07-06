from bluesky.callbacks.core import CallbackBase
from .waterfall import Waterfall

class LiveWaterfall(CallbackBase):
    """
    Stream 2D images in a cross-section viewer.

    Parameters
    ----------
    field : string
        name of data field in an Event
    """

    def __init__(self, field, *, fs=None):
        import matplotlib.pyplot as plt
        super().__init__()
        self.field = field
        self.fig = plt.figure()
        self.wf = Waterfall(fig=self.fig)
        if fs is None:
            import filestore.api as fs
        self.fs = fs
        self.i = 0

    def event(self, doc):
        if 'filled' not in doc.keys() or \
                        doc['filled'].get(self.field, False) is False:
            uid = doc['data'][self.field]
            data = self.fs.retrieve(uid)
        else:
            data = doc['data'][self.field]
        self.update(data)
        super().event(doc)

    def update(self, data):
        self.wf.update([self.i], [data])
        self.i += 1
