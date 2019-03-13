import matplotlib.pyplot as plt
from bluesky.callbacks.core import CallbackBase

from .waterfall import Waterfall


class LiveWaterfall(CallbackBase):
    """
    Stream 1D line data in a waterfall viewer.
    """

    def __init__(self):
        super().__init__()
        self.wfs = {}
        self.units = None
        self.in_dep_shapes = {}
        self.dim_names = {}
        self.dep_shapes = {}

    def start(self, doc):
        dimensions = doc.get("hints", {}).get("dimensions", [])
        if dimensions:
            self.dim_names = [
                d[0][0]
                for d in dimensions
                if d[0][0] != "time"
            ]

    def descriptor(self, doc):
        self.in_dep_shapes = {
            n: doc["data_keys"][n]["shape"] for n in self.dim_names
        }
        self.dep_shapes = {
            n: doc["data_keys"][n]["shape"]
            for n in set(self.dim_names) ^ set(doc["data_keys"])
        }
        for one_d_ind_var in [
            k for k, v in self.in_dep_shapes.items() if len(v) == 1
        ]:
            for one_d_dep_var in [
                k for k, v in self.dep_shapes.items() if len(v) == 1
            ]:
                fig = plt.figure(f"{one_d_ind_var} vs. {one_d_dep_var}")
                # if not in waterfall plots already make one, else clear it
                if (one_d_ind_var, one_d_dep_var) not in self.wfs:
                    self.wfs[(one_d_ind_var, one_d_dep_var)] = Waterfall(
                        fig,
                        unit=(
                            f"{one_d_ind_var} ({doc['data_keys'][one_d_ind_var].get('units', 'arb')})",
                            (
                                f"{one_d_dep_var} ({doc['data_keys'][one_d_dep_var].get('units','arb')})"
                            ),
                        ),
                    )
                else:
                    self.wfs[(one_d_ind_var, one_d_dep_var)].clear()

    def event(self, doc):
        super().event(doc)
        for one_d_ind_var in [
            k for k, v in self.in_dep_shapes.items() if len(v) == 1
        ]:
            for one_d_dep_var in [
                k for k, v in self.dep_shapes.items() if len(v) == 1
            ]:
                y = doc["data"].get(one_d_dep_var, None)
                x = doc["data"].get(one_d_ind_var, None)
                if x is not None and y is not None:
                    # TODO: use actual indep vars in legend.
                    self.update(
                        (x, y),
                        self.wfs[(one_d_ind_var, one_d_dep_var)],
                        doc["seq_num"],
                    )

    def update(self, data, wf, i):
        wf.update(key_list=[i], int_data_list=[data])
