from cobaya.likelihood import Likelihood
from cobaya.model import get_model
import numpy as np
import matplotlib.pyplot as plt

zarr = np.linspace(0, 2, 40)
class DummyLike(Likelihood):
    def initialize(self):
        self.stop_at_error = True

    def get_requirements(self):

        return {
            # 'power': {},
            # 'MF': {},
            'Pk_interpolator': {
                "z": zarr,
                "k_max": 5.0,
                "nonlinear": False,
                "vars_pairs": [["delta_tot", "delta_tot"]],
            }}

    def logp(self, **params):
        mf = self.theory.get_result('MF')

        pk = self.theory.get_Pk_interpolator(nonlinear=False)
        plt.plot(mf.k, pk(0, mf.k)[0])
        plt.xscale('log')
        plt.yscale('log')
        plt.xlim(0, 1)
        plt.show()
        return mf.dndm.sum()


info = {
    "debug": True,
    "params": {
        "omegabh2": 0.02225,
        "omegach2": 0.1198,
        "H0": 67.3,
        "tau": 0.06,
        "As": 2.2e-9,
        "ns": 0.96,
    },
    "likelihood": {
        'test_likelihood': DummyLike
    },
    "theory": {
        "classy": {
            # "extra_args": {},
            'stop_at_error': True,
        },
        "cobayahacks.theories.hmf": {
            "zarr": zarr,
            "hmf_kwargs": {}
        }
    },
}

m = get_model(info)
print(m.loglike())




