import yaml
import numpy as np
from pathlib import Path
import pandas as pd
import hvplot.pandas

import ares
from millicharge.params import LCDMParams, DmeffParams, ARESParams


def get_ares_params(info, **kwargs):
    """
    info : dictionary of arguments given by name 
    kwargs: dictionary of keyword argument given by 'all' in the yaml
    """
    ares_kws = {**kwargs, **dict(info)} # takes info's values for overlapping keys  
    cosmo_kwargs = {}
    cosmo_kwargs["zmax"] = ares_kws.get('initial_redshift', 100)
    include_dm = ares_kws.get('include_dm', False)

    if include_dm:
        for k in ["sigma_dmeff", "m_dmeff"]:
            if k in ares_kws:
                cosmo_kwargs[k] = float(ares_kws.get(k))
            else:
                print('using default values for {}'.format(k)) # TODO: remove when tests added
        cosmo_params = DmeffParams(**cosmo_kwargs)
    else:
        cosmo_params = LCDMParams(**cosmo_kwargs)
    return ARESParams(cosmo_params, **ares_kws)


def get_global_sim(info, **kwargs):
    ares_params = get_ares_params(info, **kwargs)
    return ares.simulations.Global21cm(**ares_params.all_kwargs)


def test_sim(sim):
    halos = sim.pops[0].halos
    for attr in ["tab_k_lin", "tab_ps_lin", "tab_ngtm", "tab_M"]:
        val = getattr(halos, attr)
        try:
            assert np.isnan(val).sum() == 0
        except AssertionError:
            raise(f'Failed at {attr}, which has some nans.')


class Worker:
    def __init__(self, output_root, clobber=True):
        self.output_root = Path(output_root)
        if not self.output_root.exists():
            self.output_root.mkdir()

        self.clobber = clobber

    def work(self, name, sim):
        print(f'running {name} simulation...')
        sim.run()

        path = self.output_root.joinpath(name)
        sim.save(path, clobber=self.clobber)
        print(f'{name} sim saved to {path}')

    def __call__(self, task):
        name, sim = task
        return self.work(name, sim)


class SimGroup:
    def __init__(self, path):
        self.path = Path(path)
        self.name = self.path.stem

        self.info = yaml.safe_load(open(self.path))

        self._global_sims = None
        self._analysis = None

    def __getitem__(self, item):
        return self.global_sims[item]

    def _get_global_sims(self):
        """Load entire YAML file
        """
        return {
            name: get_global_sim(self.info[name], **self.info["all"])
            for name in self.info.keys()
            if name != "all"
        }

    @property
    def global_sims(self):
        if self._global_sims is None:
            self._global_sims = self._get_global_sims()
        return self._global_sims

    @property
    def analysis(self):
        if self._analysis is None:
            self._analysis = {
                name: ares.analysis.Global21cm(str(Path(self.name).joinpath(name)))
                for name in self.info.keys()
                if name != "all"
            }
        return self._analysis

    def run(self, pool=None):
        map_fn = map if pool is None else pool.map

        worker = Worker(self.name)
        for r in map_fn(worker, self.global_sims.items()):
            pass

    def global_signature(self, ax=None, figsize=(10, 8), **kwargs):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        else:
            raise NotImplementedError

        for name, sim in self.analysis.items():
            label = self.info[name]['label']
            sim.GlobalSignature(ax=ax, label=label, **kwargs)

        ax.legend()
        return fig

    def _label_to_latex(self, name):
        sigma_dmeff = self.info[name]['sigma_dmeff']
        m_dmeff = self.info[name]['m_dmeff']
        return r'$\sigma_{\chi} =' + str(sigma_dmeff) + r'$; $m_{\chi} =' + str(m_dmeff) + '$'

    def fixed_sigma_gs(self, sigma, ax=None, figsize=(10, 8)):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        else:
            raise NotImplementedError

        for name, sim in self.analysis.items():
            if self.info[name]['sigma_dmeff'] == sigma:
                label = self._label_to_latex(name)
                sim.GlobalSignature(ax=ax, label=label)

        ax.legend()
        return fig

    def fixed_mass_gs(self, mass, ax=None, figsize=(10, 8)):
        if ax is None:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 1, figsize=figsize)
        else:
            raise NotImplementedError

        for name, sim in self.analysis.items():
            if math.isclose(self.info[name]['m_dmeff'], mass):
                label = self._label_to_latex(name)
                sim.GlobalSignature(ax=ax, label=label)
                
        ax.legend()
        return fig

    def history_df(self, name):
        history = self.analysis[name].history
        return pd.DataFrame({k: history[k] for k in history if len(history[k]) == len(history['z'])})

    def history_plot(self, name, component):
        df = self.history_df(name)
        return df.hvplot('z', component, logx=True, logy=True)

    def test(self):
        for name, sim in self.global_sims.items():
            test_sim(sim)

