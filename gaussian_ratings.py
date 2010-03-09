import rating
import numpy as np
from numpy import sin, cos, mean, std, arange, dot, hypot, arctan2, exp, log, pi
from numpy.fft import rfft
import scipy.optimize


import fit_gaussian
from profile_ratings import ProfileRating


class GaussianRating(ProfileRating):
    def __init__(self, DBconn, name, version, description):
        ProfileRating.__init__(self,DBconn,name,version,description)

    def rate_profile(self,hdr,candidate,profile,std,cache):
        if "gaussian" in cache:
            G = cache["gaussian"]
        else:
            G = fit_gaussian.fit_gaussian(profile)
            cache["gaussian"] = G
        return self.rate_gaussian_profile(hdr,candidate,profile,std,G,cache)

    def rate_gaussian_profile(self,hdr,candidate,profile,std,G,cache):
        pass


class GaussianHeight(GaussianRating):
    def __init__(self, DBconn):
        GaussianRating.__init__(self, DBconn,
            "Gaussian Height",
            5,
            """Compute the height of the best-fit Gaussian over the RMS amplitude.

            The function being fit is not actually a Gaussian, it's a von Mises
            distribution (exp(k*cos(theta)))
""")

    def rate_gaussian_profile(self,hdr,candidate,profile,std,G,cache):
        return G.amplitude(len(profile))/np.std(profile-G.histogram(len(profile)))

class GaussianWidth(GaussianRating):
    def __init__(self, DBconn):
        GaussianRating.__init__(self, DBconn,
            "Gaussian Width",
            4,
            """Compute the full width at half maxiumum of the best-fit Gaussian.

            The function being fit is not actually a Gaussian, it's a von Mises
            distribution (exp(k*cos(theta)))
""")

    def rate_gaussian_profile(self,hdr,candidate,profile,std,G,cache):
        return G.fwhm()

class GaussianPhase(GaussianRating):
    def __init__(self, DBconn):
        GaussianRating.__init__(self, DBconn,
            "Gaussian Phase",
            4,
            """Compute the peak phase of the best-fit Gaussian.

            The function being fit is not actually a Gaussian, it's a von Mises
            distribution (exp(k*cos(theta)))
""")

    def rate_gaussian_profile(self,hdr,candidate,profile,std,G,cache):
        return G.mu

class GaussianSignificance(GaussianRating):
    def __init__(self, DBconn):
        GaussianRating.__init__(self, DBconn,
            "Gaussian Sig",
            1,
            """Compute the significance of the best-fit Gaussian.

            The function being fit is not actually a Gaussian, it's a von Mises
            distribution (exp(k*cos(theta))). This compares the Gaussian height
            to the expected standard deviation of an average over the 
            Gaussian width.

""")

    def rate_gaussian_profile(self,hdr,candidate,profile,std,G,cache):
        return G.amplitude(len(profile))/(std*(G.fwhm()/(1./len(profile)))**(0.5))

if __name__=='__main__':
    D = rating.usual_database()
    rating.run(D, [
        GaussianHeight(D),
        GaussianWidth(D),
        GaussianPhase(D),
        ])

