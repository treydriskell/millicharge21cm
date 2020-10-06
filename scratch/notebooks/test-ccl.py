import matplotlib.pyplot as plt
import numpy as np
import classy

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


m_dmeff = 1.0  # GeV
sigma_dmeff = 1e-41  # cm^2
Vrel_dmeff = 30 # km/s at z ~ 1010
params = LCDM.class_params()

z_pk = 60.
params.update({'z_pk': z_pk})

cl = classy.Class()
cl.set(params)
cl.compute()

import pyccl as ccl

cosmo = ccl.Cosmology(Omega_c=params['omega_cdm'], 
                      Omega_b=params['omega_b'],
                      h=params['h'],
                      n_s=params['n_s'], A_s=params['A_s'])

# trying to adapt from here: https://github.com/damonge/ShCl_like/blob/0350b0cca5de51cd92efb8e27be292bbbb449bce/shcl_like/clccl.py#L141
z_bg = np.concatenate((np.linspace(0, 10, 100), np.geomspace(10, 1500, 50)))

a = 1/(1 + z_bg[::-1])
distance = cl.z_of_r(z_bg)
distance = np.flip(distance)

hubble_z = np.array([cl.Hubble(z) for z in z_bg])
H0 = hubble_z[0]
E_of_z = hubble_z / H0
E_of_z = np.flip(E_of_z)

kmax = 100
k_arr = np.logspace(-5, 2, 1000)
z_pk = np.array([60.,])
class_pk_lin = cl.get_pk_array(k_arr, z_pk, 1000, 1, False)

print('setting background quantities')
cosmo._set_background_from_arrays(a_array=a, chi_array=distance, hoh0_array=E_of_z)

print(f'setting p(k) at z={z_pk} with {class_pk_lin}')
cosmo._set_linear_power_from_arrays(1./(1 + z_pk), k_arr, class_pk_lin)

print('computing HMF:')
# compute HMF
mdef = ccl.halos.MassDef(500, 'critical')
hmf = ccl.halos.MassFuncTinker08(cosmo, mass_def=mdef)
