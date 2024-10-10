import pyPamtra
import numpy as np
import matplotlib.pyplot as plt
import sys
import math


def RStoTB(P,z,T1,RH,Q):
"""
Returns brightness temperature simulated through PAMTRA for an zenith-pointing geometry @89 GHz.
"""
    T = [TT+273.15 for TT in T1]
    q = [[hq] for hq in Q]    
    pam = pyPamtra.pyPamtra()

    # choose hydrometeor distribution
    pam.df.addHydrometeor(('cwc_q',-99.,1,-99.,-99.,-99.,-99.,-99.,3,1,'mono',-99.,-99.,-99.,-99.,2e-5,-99.,'mie-sphere', 'khvorostyanov01_drops',-99.))
    pam.createProfile(hgt_lev=z,temp_lev=T,press_lev=P,relhum_lev=RH)
    pam.p["hydro_q"][:] = q[1:]

	# only passive simulation (radiometer)
    pam.nmlSet["active"] = False
    # set the frequency (here 89)
    pam.runPamtra(89)

	# Adjust this depending on the geometry
    angleIndex = np.where(0==pam.r['angles_deg'])[0][0]
    freqIndex = 0
    StokesIndex = 1
    levelIndex=1


    tb = pam.r["tb"][:,:,levelIndex,angleIndex,freqIndex,StokesIndex].tolist()
    
    return tb
