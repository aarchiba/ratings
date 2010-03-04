import rating
import numpy as np
from numpy import sin, cos, mean, std, arange, dot, hypot, arctan2, exp, log, pi
from numpy.fft import rfft
import scipy.optimize

import copy

class ProfileRating(rating.DatabaseRater):
    def __init__(self, DBconn, name, version, description):
        rating.DatabaseRater.__init__(self,DBconn,name,version,description,with_files=True)

    def rate_candidate(self,hdr,candidate,pfd_file=None,cache=None):
        if "std" in cache:
            std = cache["std"]
        else:
            std = np.sqrt(np.mean(np.var(pfd_file.profs,axis=-1)))*np.sqrt(pfd_file.nsub*pfd_file.npart)
            cache["std"] = std
        if "profile" in cache:
            prof = cache["profile"]
        else:
            if "dedispersed_pfd" in cache:
                pfd_file = cache["dedispersed_pfd"]
            else:
                oldpfd = pfd_file
                pfd_file = copy.deepcopy(pfd_file)
                pfd_file.dedisperse(candidate["dm"])
                #if np.all(oldpfd.profs == pfd_file.profs):
                pfd_file.profs[0,0,0]+=1
                if np.all(oldpfd.profs == pfd_file.profs):
                    raise ValueError("copy failed to copy the pfd file")
                pfd_file.profs[0,0,0]-=1
                cache["dedispersed_pfd"] = pfd_file

            prof = pfd_file.combine_profs(1,1)[0,0]
            prof -= np.mean(prof)
            cache["profile"] = prof
        return self.rate_profile(hdr,candidate,prof,std,cache)

    def rate_profile(self,hdr,candidate,profile,std,cache):
        raise NotImplementedError


class DutyCycle(ProfileRating):
    def __init__(self, DBconn):
        ProfileRating.__init__(self, DBconn,
            "Duty cycle",
            1,
            """Compute the duty cycle, that is, the fraction of profile
bins in which the value is more than (max+mean)/2.""")

    def rate_profile(self,hdr,candidate,profile,std,cache):
        return np.sum(profile>(np.amax(profile)+np.mean(profile))/2.)/float(len(profile))

class PeakOverRMS(ProfileRating):
    def __init__(self, DBconn):
        ProfileRating.__init__(self, DBconn,
            "Peak over RMS",
            1,
            """Compute the peak amplitude divided by the RMS amplitude.

Specifically, compute (max(profile)-mean(profile))/std(profile).
""")

    def rate_profile(self,hdr,candidate,profile,std,cache):
        return (np.amax(profile)-np.mean(profile))/np.std(profile)

if __name__=='__main__':
    D = rating.usual_database()
    rating.run(D,
               [DutyCycle(D), 
                PeakOverRMS(D),
               ])

class PrepfoldSigmaRating(rating.DatabaseRater):
    def __init__(self, DBconn):
	rating.DatabaseRater.__init__(self, DBconn, \
	    version = 3, \
	    name = "Prepfold Sigma", \
	    description = "A re-calculation of the sigma value reported on " \
			  "prepfold plots.\n\nCandidates where P(noise) ~ 0 " \
			  "are rated as 99 since a proper sigma value " \
			  "cannot be computed.", \
	    with_files = True, \
	    with_bestprof = True)

    def rate_profile(self, hdr, candidate, profile, std, cache):
        chi2 = np.sum((profile-np.mean(profile))**2/std**2)
        df = len(profile)-1

	return min(-scipy.stats.norm(scipy.stats.chi2(df).sf(chi2)),99)

