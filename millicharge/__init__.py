from astropy.cosmology import Planck18_arXiv_v2 as Planck

h = Planck.h
class LCDM:
    h = h
    H0 = Planck.H0.value
    omega_b = Planck.Ob0 * h ** 2
    omega_cdm = (Planck.Om0 - Planck.Ob0) * h ** 2
    omega_nu = Planck.Onu0
    omega_k = Planck.Ok0

    m_ncdm = sum(Planck.m_nu).value
    Neff = Planck.Neff
    N_ncdm = 1
    N_ur = Planck.Neff - N_ncdm

    Tcmb = Planck.Tcmb0.value
    A_s = 2.097e-9
    tau_reio = 0.0540
    n_s = 0.9652
    YHe = 0.24537116583825905
    reion_exponent = 1.5
    reion_width = 0.5

    @classmethod
    def class_params(self):
        return {
            'h': self.h, 'omega_b': self.omega_b, 'omega_cdm': self.omega_cdm,
            'Omega_k': self.omega_k, 'N_ur': self.N_ur, 'N_ncdm': self.N_ncdm,
            'm_ncdm': self.m_ncdm, 'A_s': self.A_s, 'n_s': self.n_s,
            'T_cmb': self.Tcmb, 'tau_reio': self.tau_reio, 'YHe': self.YHe,
            'reionization_exponent': self.reion_exponent,
            'reionization_width': self.reion_width, 'P_k_max_1/Mpc': 200,
            'output': 'dTk,mPk,tCl',
        }

