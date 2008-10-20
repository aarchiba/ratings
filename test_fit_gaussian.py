import numpy as np
from numpy.testing import *

import fit_gaussian

def check_fit_quality(G,noise_amp,n):
    true = G.histogram(n)
    noise = np.random.randn(n)*noise_amp
    data = true + noise
    Gf = fit_gaussian.fit_gaussian(data)

    assert np.std(Gf.histogram(n)-true)<2*noise_amp/np.sqrt(n)


def test_fit_quality():

    for k in [0.1,1,3,10,100,1000,10000]:
        yield check_fit_quality(fit_gaussian.GaussianProfile(k), 0.01, 128)

    for mu in [0,0.1,0.3,0.7]:
        yield check_fit_quality(fit_gaussian.GaussianProfile(5,mu=mu), 0.01, 128)

    for amp in [1e-3,1,1e3]:
        yield check_fit_quality(fit_gaussian.GaussianProfile(5,a=amp), 0.01*amp, 128)

    for offset in [1,-1,1000,-1000]:
        yield check_fit_quality(fit_gaussian.GaussianProfile(5,b=offset), 0.01, 128)

