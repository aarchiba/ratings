import numpy as np
from numpy.fft import rfft, irfft

import prepfold
import psr_utils

class Folds(prepfold.pfd):
    def __init__(self,pfd):
        self.pfd = pfd
        self.original_fold_p = self.pfd.fold_p1
        self.original_fold_pdot = self.pfd.fold_p2


        self.current_p = self.original_fold_p
        self.current_pdot = self.original_fold_pdot
        self.current_dm = 0.

        self.best_p = self.pfd.topo_p1
        self.best_pdot = self.pfd.topo_p2
        self.best_dm = self.pfd.bestdm

        self.profs = np.copy(self.pfd.profs)

    def shift(self,p=None,pdot=None,dm=None):
        if dm is None:
            dm = self.current_dm
        if p is None:
            p = self.current_p
        if pdot is None:
            pdot = self.current_pdot

        f = rfft(self.profs,axis=-1)

        # the sample at phase p is moved to phase p-dmdelays
        dmdelays = (psr_utils.delay_from_DM(dm,self.pfd.subfreqs) -
                    psr_utils.delay_from_DM(self.current_dm,self.pfd.subfreqs))/self.original_fold_p
        
        start_times = self.pfd.start_secs
        pdelays = (start_times/self.original_fold_p) * (p-self.current_p)/self.original_fold_p
        pdotdelays = ((pdot-self.current_pdot)*start_times**2/2.)/self.original_fold_p
        
        f *= np.exp((2.j*np.pi)*
            dmdelays[np.newaxis,:,np.newaxis]*
            np.arange(f.shape[-1])[np.newaxis,np.newaxis,:])
        f *= np.exp((2.j*np.pi)*
            (pdelays+pdotdelays)[:,np.newaxis,np.newaxis]*
            np.arange(f.shape[-1])[np.newaxis,np.newaxis,:])

        self.profs = irfft(f)
        self.current_p = p
        self.current_dm = dm
        self.current_pdt = pdot
