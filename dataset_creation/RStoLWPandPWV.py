import numpy as np
import math


def RStoLWPandPWV(P1,z,T1,RH1,Qv1,alpha=0.59,beta=1.37):
""" Computes LWP and PWV from a given radiosonde profile with Salonen cloud model adapted with Mattioli 2009"""
    ### Prepare the radiosonde data
    # sort for increasing z (sometimes not already the case)
    P = [p for _, p in sorted(zip(z,P1))]
    T = [temp for _, temp in sorted(zip(z,T1))]
    RH = [rh for _, rh in sorted(zip(z,RH1))]
    Qv = [qv for _, qv in sorted(zip(z,Qv1))] #Qv in RS is in g/kg
    Rd = 287.058 # specific gas constant for dry air, J/(kg.K)
    z.sort()
    
    N = len(z)
    rho = [P[i]/(Rd*(T[i]+273.15)) for i in range(N)]

    # initialize the containers
    LWC = [0 for i in range(N)]        
    WVC = [rho[i]*Qv[i]*1e-3 for i in range(N)]
    
    ####
    # cloud layer 
    # Salonen critical humidity threshold    
    sigma = [p/P[0] for p in P]
    thres_S = [1-alpha*s*(1-s)*(1+beta*(s-0.5)) for s in sigma]
    icloud = [] # indices which are identified as belonging to a cloud layer
    for i in range(N):
        if RH[i]>=thres_S[i]*100:
            icloud.append(i)
                    
      
    # define cloud layers (needed for LWC modeling)
    if len(icloud)>1:
        k = 0
        ibasecloud = [] # store the index corresponding to base of cloud layer
        hcloud = [] # store the height of the cloud layer (in terms of indices)
        icorrbase = [float('nan') for i in icloud]
        while k < len(icloud):
            h = 1
            if k+h >= len(icloud):
                break
            while icloud[k+h]==icloud[k]+h: # i.e. no gap in the cloud layer
                h = h+1
                if k+h >= len(icloud):
                    break
            ibasecloud.append(icloud[k])
            hcloud.append(h)
            k = k+h
        

        for k in range(len(icloud)):
            for j in range(len(ibasecloud)-1):
                if icloud[k]>=ibasecloud[j] and icloud[k] < ibasecloud[j+1]:
                    icorrbase[k]=ibasecloud[j]
            if icloud[k]>=ibasecloud[-1]:
                icorrbase[k]=ibasecloud[-1]
    
    
    ###
    # liquid water in the cloud
    
    # temperature-dependent model (from Salonen) to compute LWC profile inside the cloud layers
    wc = [0 for i in range(N)] # store water content
    fw = [0 for i in range(N)] # variable in Salonen model
    
    wo = 0.17
    c = 0.04
    a = 1.
    hr = 1.5e3

    if len(icloud)>1:        
        for k in range(len(icloud)):
            if T[icloud[k]]>=0:
                wc[icloud[k]] = wo*((z[icloud[k]]-z[icorrbase[k]])/hr)**a*(1+c*T[icloud[k]])
                fw[icloud[k]] = 1
            else:
                wc[icloud[k]] = wo*((z[icloud[k]]-z[icorrbase[k]])/hr)**a*(math.exp(c*T[icloud[k]]))
                if T[icloud[k]]>=-20:
                    fw[icloud[k]] = 1+T[icloud[k]]/20

            LWC[icloud[k]] = wc[icloud[k]]*fw[icloud[k]]
        
    # Compute integral (LWP and PWV)    
    LWP = sum([LWC[i]*(z[i+1]-z[i]) for i in range(len(z)-1)])
    PWV = sum([WVC[i]*(z[i+1]-z[i]) for i in range(len(z)-1)])
    

    ### Adding Q variables for PAMTRA input

    Q = [LWC[i]/rho[i]*1e-3 for i in range(N)]

    return P,z,T,RH,PWV,LWP,Q
