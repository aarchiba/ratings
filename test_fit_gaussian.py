import numpy as np

import fit_gaussian

def test_nothing():
    n = 128
    data = np.random.randn(n)
    Gf = fit_gaussian.fit_gaussian(data)

    assert Gf.amplitude() < 4
    assert np.std(Gf.histogram(n)-data)<4


def check_fit_quality(G,noise_amp,n):
    true = G.histogram(n)
    noise = np.random.randn(n)*noise_amp*G.amplitude()
    data = true + noise
    Gf = fit_gaussian.fit_gaussian(data)

    assert np.abs(Gf.amplitude()-G.amplitude())/G.amplitude()<0.01


def test_fit_quality():

    for k in [0.1,1,3,10,100,1000,10000]:
        yield check_fit_quality, fit_gaussian.GaussianProfile(k), 0.0, 128

    for mu in [0,0.1,0.3,0.7]:
        yield check_fit_quality, fit_gaussian.GaussianProfile(5,mu=mu), 0.0, 128

    for amp in [1e-3,1,1e3]:
        yield check_fit_quality, fit_gaussian.GaussianProfile(5,a=amp), 0.0, 128

    for offset in [1,-1,1000,-1000]:
        yield check_fit_quality, fit_gaussian.GaussianProfile(5,b=offset), 0.0, 128

