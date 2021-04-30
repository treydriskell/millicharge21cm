from astropy.cosmology import Planck18_arXiv_v2 as Planck
import classy


class LCDMParams:
    def __init__(self, kmax=200, zmax=100, **kwargs):
        self.kmax = kmax
        self.zmax = zmax

        self.h = Planck.h
        self.H0 = Planck.H0.value
        self.omega_b = Planck.Ob0 * Planck.h ** 2
        self.omega_cdm = (Planck.Om0 - Planck.Ob0) * Planck.h ** 2
        self.omega_nu = Planck.Onu0
        self.omega_k = Planck.Ok0

        self.m_ncdm = sum(Planck.m_nu).value
        self.Neff = Planck.Neff
        self.N_ncdm = 1
        self.N_ur = Planck.Neff - self.N_ncdm

        self.Tcmb = Planck.Tcmb0.value
        self.A_s = 2.097e-9
        self.tau_reio = 0.0540
        self.n_s = 0.9652
        self.YHe = 0.24537116583825905
        self.reion_exponent = 1.5
        self.reion_width = 0.5

        self.__dict__.update(kwargs)

    @property
    def class_params(self):
        return {
            "h": self.h,
            "omega_b": self.omega_b,
            "omega_cdm": self.omega_cdm,
            "Omega_k": self.omega_k,
            "N_ur": self.N_ur,
            "N_ncdm": self.N_ncdm,
            "m_ncdm": self.m_ncdm,
            "A_s": self.A_s,
            "n_s": self.n_s,
            "T_cmb": self.Tcmb,
            "tau_reio": self.tau_reio,
            "YHe": self.YHe,
            "reionization_exponent": self.reion_exponent,
            "reionization_width": self.reion_width,
            "P_k_max_1/Mpc": self.kmax,
            "output": "dTk,mPk,tCl",
            "z_max_pk": self.zmax,
        }


class DMBParams(LCDMParams):
    def __init__(self, **kwargs):
        super().__init__()

        # Defaults
        self.omega_dmb = self.omega_cdm
        self.omega_cdm = 1e-10
        self.m_dmb = 1.0  # GeV
        self.sigma_dmb = 1e-40  # cm^2
        self.Vrel_dmb = 30  # km/s at z ~ 1010
        self.n_dmb = -4

        self.__dict__.update(kwargs)

    @property
    def class_params(self):
        pars = super().class_params
        pars.update({k: getattr(self, k) for k in ["omega_dmb", "m_dmb", "sigma_dmb", "n_dmb", "Vrel_dmb"]})
        return pars


class ARESParams:
    def __init__(
        self,
        cosmo=None,
        use_classy_pk=False,
        include_dm=False,
        verbose=True,
        initial_redshift=100,
        initial_timestep=0.001,
        cosmology_package="ccl",
        hmf_package="ccl",
        hmf_model="Tinker10",
        restricted_timestep=["ions", "neutrals", "electrons", "temperature", "hubble", "idm"],
        epsilon_dt=0.05 * 0.02,
        hmf_load=False,
        hmf_zmin=0.0,
        **kwargs
    ):
        if cosmo is None:
            cosmo = LCDMParams()
        self.cosmo = cosmo
        self.use_classy_pk = use_classy_pk

        self.kwargs = {}
        for kw in [
            "include_dm",
            "verbose",
            "initial_redshift",
            "initial_timestep",
            "cosmology_package",
            "hmf_package",
            "hmf_model",
            "restricted_timestep",
            "epsilon_dt",
            "hmf_load",
            "hmf_zmin",
        ]:
            self.kwargs[kw] = kwargs.get(kw, eval(kw))

        if "pop_ion_src_igm{1}" in kwargs.keys():
            self.kwargs["pop_ion_src_igm{1}"] = kwargs["pop_ion_src_igm{1}"]
            
        self.include_dm = self.kwargs["include_dm"]
        if self.include_dm and not isinstance(cosmo, DMBParams):
            raise ValueError("Must pass DMBParams if including DM.")

        if not self.include_dm and isinstance(cosmo, DMBParams):
            self.include_dm = True
            self.kwargs["include_dm"] = True
            # print("Using DMBParams.  Setting include_dm to True.")

        self._classy = None

    @property
    def all_kwargs(self):
        kwargs = self.kwargs.copy()
        kwargs.update(self.cosmo_params)

        if self.use_classy_pk:
            kwargs["cosmology_helper"] = self.classy
            kwargs["kmax"] = self.cosmo.kmax
        return kwargs

    @property
    def classy(self):
        if self._classy is None:
            self._classy = classy.Class()
            self._classy.set(self.cosmo.class_params)
            self._classy.compute()
        return self._classy

    @property
    def cosmo_params(self):
        params = {
            "omega_m_0": (self.cosmo.omega_cdm + self.cosmo.omega_b) / self.cosmo.h ** 2,
            "omega_b_0": self.cosmo.omega_b / self.cosmo.h ** 2,
            "hubble_0": self.cosmo.h,
            "primordial_index": self.cosmo.n_s,
            "cmb_temp_0": self.cosmo.Tcmb,
        }
        if self.include_dm:

            thermo = self.classy.get_thermodynamics()
            inputs = {
                "z": thermo["z"],
                "xe": thermo["x_e"],
                "Tk": thermo["Tb [K]"],
                "Tchi": thermo["T_dmb"],
                "Vchib": self.cosmo.Vrel_dmb * 1e5 * self.kwargs["initial_redshift"] / 1010,
            }

            params.update(
                dict(
                    cosmology_name="user",
                    cosmology_inits=inputs,
                    m_dmeff=self.cosmo.m_dmb,
                    sigma_dmeff=self.cosmo.sigma_dmb,
                    npow_dmb=self.cosmo.n_dmb,
                )
            )
            params["omega_m_0"] = (self.cosmo.omega_dmb + self.cosmo.omega_b) / self.cosmo.h ** 2

        return params
