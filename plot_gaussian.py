import numpy as np
import pylab as plt
import fit_gaussian

def plot_residuals(data):

    n = len(data)
    xs = np.arange(n)/float(n)

    test_ks = np.exp(np.linspace(np.log(0.1),np.log(1000),1000))
    G = fit_gaussian.fit_gaussian(data)

    plt.figure()
    resids = [fit_gaussian.rms_residual(k,data) for k in test_ks]
    plt.loglog(test_ks,resids,color="green")
    best_k = test_ks[np.argmin(resids)]
    plt.axvline(best_k,color="green")
    plt.axvline(G.k,color="cyan")

    plt.figure()
    mue, ae, be = fit_gaussian.fit_all_but_k(best_k, data)
    plt.plot(xs, data, color="black", label="data")
    plt.plot(xs, (ae*fit_gaussian.vonmises_histogram(best_k,mue,n)+be),
            color="green", label="exhaustive best fit")
    plt.plot(xs, G.histogram(n), color="cyan", label="best fit")
    plt.plot([G.mu,G.mu],[G.b,G.b+G.amplitude(n)], color="red", label="height")

    print "Amplitude over RMS:", G.amplitude(n)/np.std(data-G.histogram(n))

    plt.legend(loc="best")

    return data

if __name__=='__main__':
    import scipy.io
    plot_residuals(scipy.io.read_array("noisy-1"))
    plt.figure()
    for factor in [1,2,4,8]:
        plt.plot(fit_gaussian.vonmises_histogram(1000,0.5,64,factor=factor),     label="factor %d" % factor)
    plt.legend(loc="best")
    plt.show()
