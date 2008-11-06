import numpy as np
import scipy.stats
from numpy.fft import rfft, irfft
from scipy.special import ive

def vonmises_coefficient(k,m):
    return ive(m,k)/ive(0,k)
def vonmises_values(k,mu,xs):
    D = scipy.stats.vonmises(k,scale=1./(2*np.pi))
    return D.pdf((xs-mu)%1)
def vonmises_histogram(k,mu,n,factor=4):
    if n%1:
        raise ValueError("n must be even")
    m = ((n*factor)//2+1)
    coeffs = vonmises_coefficient(k,np.arange(m))*np.exp(-2.j*np.pi*mu*np.arange(m))*n*factor
    longhist = 1.+irfft(coeffs*(np.exp(2.j*np.pi*1./n*np.arange(m))-1)/(np.maximum(np.arange(m),1)*2.j*np.pi))*n*factor
    return np.mean(np.reshape(longhist,(n,factor)),axis=-1)/factor

def fit_all_but_k(k,data):
    n = len(data)
    F = rfft(data)
    nup = 16*n
    corr = irfft(F*vonmises_coefficient(k,np.arange(len(F))),nup)
    mu = np.argmax(corr)/float(nup)

    x = vonmises_histogram(k,mu,n)

    data = data - np.mean(data)
    x = x - np.mean(x)
    a = np.dot(data,x)/np.dot(x,x)
    
    b = np.mean(data) - a*np.mean(x)

    return mu, a, b

def rms_residual(k,data):
    n = len(data)
    mu, a, b = fit_all_but_k(k, data)

    return np.sqrt(np.mean((data-(a*vonmises_histogram(k,mu,n)+b))**2))



class GaussianProfile:

    def __init__(self,k,mu=0.,a=1.,b=0.):
        if k<0:
            raise ValueError("Negative values of k simply shift the phase by 0.5; please do not supply them")
        self.k = float(k)
        self.mu = float(mu)
        self.a = float(a)
        self.b = float(b)

    def __repr__(self):
        return "<GaussianProfile k=%g mu=%g a=%g b=%g>" % (self.k, self.mu, self.a, self.b)

    def max(self):
        return self(self.mu)
    def min(self):
        return self(self.mu+0.5)
    def amplitude(self,n=None,peak_to_peak=True):
        if n is None:
            if peak_to_peak:
                return self.max()-self.min()
            else:
                return self.max()-self.b
        else:
            h = self.histogram(n)
            if peak_to_peak:
                return np.amax(h)-np.amin(h)
            else:
                return np.amax(h)-self.b

    def area(self,peak_to_peak=True):
        if peak_to_peak:
            return self.a-self.min()
        else:
            return self.a


    def histogram(self,n):
        return self.a*vonmises_histogram(self.k,self.mu,n)+self.b

    def __call__(self,x):
        return self.a*vonmises_values(self.k,self.mu,x)+self.b

    def fwhm(self):
        s_height = (np.exp(-2*self.k)+1)/2.
        return 2*np.arccos(1+np.log(s_height)/self.k)/(2*np.pi)



def k_for_fwhm_approx(fwhm):
    return np.log(2)/(1-np.cos(np.pi*fwhm))

def fit_gaussian(profile):
    ks = [k_for_fwhm_approx(fwhm/float(len(profile))) for fwhm in range(1,len(profile)//2)]
    pos = np.argmin([rms_residual(k,profile) for k in ks])

    if pos==0:
        mid = ks[0]
        left = ks[1]
        right = 10*ks[0]
    elif pos==len(ks)-1:
        left = 0
        mid = ks[-1]
        right = ks[-2]
    else:
        left = ks[pos+1]
        mid = ks[pos]
        right = ks[pos-1]

    k = scipy.optimize.fminbound(lambda k: rms_residual(k,profile), left, right)
    print left, k, right
    print rms_residual(k,profile)

    mu, a, b = fit_all_but_k(k, profile)
    
    return GaussianProfile(k,mu,a,b)
    

def plot_residuals():
    import pylab as plt

    true_k = 8
    n = 128
    s = 10
    a = 10
    mu = 0.1

    k2 = 30
    a2 = 10
    mu2 = 0.5

    xs = np.arange(n)/float(n)
    true_prof = a*vonmises_histogram(true_k,mu,n) + a2*vonmises_histogram(k2,mu2,n)
    data = true_prof + s*np.random.randn(n)

    test_ks = np.exp(np.linspace(np.log(0.1),np.log(1000),1000))
    G = fit_gaussian(data)

    plt.figure(1)
    resids = [rms_residual(k,data) for k in test_ks]
    plt.loglog(test_ks,resids,color="green")
    plt.axvline(true_k,color="red")
    best_k = test_ks[np.argmin(resids)]
    plt.axvline(best_k,color="green")
    plt.axvline(G.k,color="cyan")

    plt.figure(2)
    mue, ae, be = fit_all_but_k(best_k, data)
    plt.plot(xs, true_prof, color="red", label="true")
    plt.plot(xs, data, color="black", label="data")
    plt.plot(xs, (ae*vonmises_histogram(best_k,mue,n)+be), color="green", label="exhaustive best fit")
    plt.plot(xs, G.histogram(n), color="cyan", label="best fit")



    plt.legend(loc="best")

    return data

if __name__=='__main__':
    import pylab as plt
    plot_residuals()
    plt.show()
