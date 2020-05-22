import classy
import camb
from astropy.cosmology import Planck15 as Planck
import numpy as np
import matplotlib.pyplot as plt

h = Planck.h
cosmo = Planck
class LCDM:
    h=h
    H0=Planck.H0.value
    omega_b=Planck.Ob0 * h**2
    omega_cdm=(Planck.Om0 - Planck.Ob0) * h**2
    omega_k=Planck.Ok0
    Neff=Planck.Neff
    Tcmb=Planck.Tcmb0.value
    A_s = 2.097e-9
    tau_reio = 0.0540
    n_s = 0.9652


# Camb initialization
camb_params = camb.CAMBparams()
camb_params.set_cosmology(
    H0=LCDM.H0, ombh2=LCDM.omega_b, omch2=LCDM.omega_cdm,
    omk=LCDM.omega_k, nnu=LCDM.Neff, TCMB=LCDM.Tcmb, tau=LCDM.tau_reio
)
camb_params.WantTransfer = True
camb_params.WantCls = True
camb_params.InitPower.set_params(ns=LCDM.n_s, As=LCDM.A_s)
camb_params.set_accuracy(
    AccuracyBoost=3.0, lAccuracyBoost=3.0, lSampleBoost=3.0,
    DoLateRadTruncation=False
)

camb_res = camb.get_results(camb_params)
camb_trans = camb.get_transfer_functions(camb_params)
camb_trans = camb_trans.get_matter_transfer_data().transfer_data[[0,6],:,0] # Returns [k, T_tot(k)]
print("Initialized CAMB")

# Class Initialization
class_params = {
    'h': LCDM.h,
    'omega_b': LCDM.omega_b,
    'omega_cdm': LCDM.omega_cdm,
    'Omega_k': LCDM.omega_k,
    'N_ur': LCDM.Neff,
    'A_s': LCDM.A_s,
    'n_s': LCDM.n_s,
    'T_cmb': LCDM.Tcmb,
    'tau_reio': LCDM.tau_reio,
    'P_k_max_1/Mpc': 100,
    'output': 'dTk,mPk,tCl'
}
cl = classy.Class()
cl.set(class_params)
cl.compute()
print("Initialized CLASS")

l, cl_class = cl.raw_cl()['ell'], cl.raw_cl()['tt']
l_fac = l*(l+1)/(2 * np.pi)
cl_class *= l_fac
cl_camb = camb_res.get_unlensed_total_cls(lmax=l[-1]).T[0]

m = l > 3
x = l[m]
y1 = cl_class[m]
y2 = cl_camb[m]

fig, (ax1,ax2) = plt.subplots(
    2, 1, figsize=(8,7),
    gridspec_kw={'height_ratios': [3,1], 'hspace': 0.05}
)

ax1.plot(x, y1, label='class')
ax1.plot(x, y2, label='camb')
ax1.set(ylabel=r'$C_\ell^{TT}$')
ax1.tick_params(axis='x', which='both', direction='in', labelbottom=False)
ax1.legend()

perc_err = 100 * (y1-y2) / ((y1 + y2)/2)
ax2.plot(x, perc_err)
ax2.set(ylabel='% Error', ylim=(-1, 2))

plt.savefig('~/Desktop/Cell_comparison.png')
plt.show()