from cobaya.theory import Theory
import numpy as np
from hmf import MassFunction
from astropy.cosmology import LambdaCDM, FLRW


class hmf(Theory):
    # params = {'omegabh2': None, 'omegach2': None, 'H0': None}

    def initialize(self):
        self._hmf_kwargs = {
            'use_splined_growth': True
        }
        self._hmf_kwargs.update(self.hmf_kwargs)
        # self.input_params = ['omegabh2', 'omegach2', 'H0']

        self.quants = ['dndm', 'rho_gtm', 'ngtm', 'power', 'growth_factor']

    def needs(self, **requirements):
        self._reqs = requirements.keys()

    def get_can_provide(self):
        return self.quants + ['MF']

    def get_requirements(self):
        print("Requirements")
        return {
            "Pk_interpolator": {
                "z": self.zarr,
                "k_max": 5.0,
                "nonlinear": False,
                "vars_pairs": [["delta_tot", "delta_tot"]],
            },
        }

    def initialize_with_params(self):
        print("params")
        pass

    def calculate(self, state, want_derived=True, **params_values_dict):
        self._hmf_kwargs['z'] = self.zarr[0]
        h = params_values_dict["H0"] / 100
        Oc = params_values_dict['omegach2'] / h**2
        Ob = params_values_dict['omegabh2'] / h**2
        Om = Oc + Ob
        Ode = 1 - Om
        self._hmf_kwargs['cosmo_params'] = {
            'H0': 100*h,
            'Om0': Om,
            'Ob0': Ob,
        }
        self.MF = MassFunction(**self._hmf_kwargs)
        pk_interp = self.provider.get_Pk_interpolator(nonlinear=False)
        for q in self.quants:
            state[q] = []
        print("HERE")
        for i, z in enumerate(self.zarr):
            self.MF.update(z=z, custom_pk=pk_interp.P(z, self.MF.k))
            for q in self.quants:
                state[q].append(getattr(self.MF, q).copy())
        state["MF"] = self.MF
        state['zs'] = self.zarr

