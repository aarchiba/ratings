import numpy as np

import rating
import prepfold_plus

class RatioRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=2,
            name="Ratio Rating",
            description="""Compare DM 0 and "best" DM

Computes the ratio of peak height for the profile dedispersed at
DM 0 divided by that for the profile dedispersed at the best-fit DM.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd):
        
        p0 = np.sum(np.sum(pfd.profs,axis=0),axis=0)
        pfd.dedisperse(candidate["dm"])
        p1 = np.sum(np.sum(pfd.profs,axis=0),axis=0)

        return (np.amax(p0)-np.mean(p0))/(np.amax(p1)-np.mean(p1))

class BroadbandRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=1,
            name="Broadbandedness",
            description="""Evaluate how broadband the signal is

Computes a normalized dot product between the average profile and every
subband, then measures how many of the results are close to 1.

Doesn't work.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd):
        pfd.dedisperse(candidate["dm"],interp=True)

        subbands = pfd.combine_profs(1,pfd.nsub)[0]
        subbands -= np.mean(subbands,axis=-1)[:,np.newaxis]
        subbands /= np.sqrt(np.mean(np.sum(subbands**2,axis=-1)))

        profile = np.mean(subbands,axis=0)
        profile -= np.mean(profile)
        profile /= np.sqrt(np.dot(profile,profile))

        dots = np.dot(subbands,profile)
        #print dots
        
        return np.mean(dots)

if __name__=='__main__':
    RatioRating(rating.usual_database()).run()
