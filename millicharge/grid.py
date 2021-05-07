from pathlib import Path
from itertools import product
import yaml

from .batch import SimGroup


def enumerated_product(*args):
    """
    https://stackoverflow.com/questions/56430745/enumerating-a-tuple-of-indices-with-itertools-product
    """
    yield from zip(product(*(range(len(x)) for x in args)), product(*args))


class SimGroupGrid(SimGroup):
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.stem

        self.grid_info = yaml.safe_load(open(self.path))

        self._info = None

        self._global_sims = None
        self._analysis = None

    @property
    def info(self):
        if self._info is None:
            self._make_info()
        return self._info

    def _make_info(self):
        d = self.grid_info

        grid_params = [k for k in d.keys() if k != "all"]

        info = dict(d)

        for idx, pars in enumerated_product(*[d[p] for p in grid_params]):
            name = "_".join([str(i) for i in idx])

            info[name] = {}

            label = ""
            for p, value in zip(grid_params, pars):
                label += f"{p} = {value}; "
                info[name][p] = value

            label = label[:-2]
            info[name]["label"] = label

        for p in grid_params:
            del info[p]

        self._info = info
