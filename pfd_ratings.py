import numpy as np

import rating
import profile_ratings
import scipy.stats as stats

import copy

class RatioRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=5,
            name="Ratio Rating",
            description="""Compare DM 0 and "best" DM

Computes the ratio of RMS height for the profile dedispersed at
DM 0 divided by that for the profile dedispersed at the best-fit DM.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
	
	# Un-dedispersed profile        
        p0 = pfd.time_vs_phase().sum(axis=0)
        p1 = profile_ratings.get_profile(cache, pfd)
        return np.std(p0)/np.std(p1)


class RatioRatingPeak(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=5,
            name="Ratio Rating Peak",
            description="""Compare DM 0 and "best" DM

Computes the ratio of peak height for the profile dedispersed at
DM 0 divided by that for the profile dedispersed at the best-fit DM.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
        
        p0 = pfd.time_vs_phase().sum(axis=0)
        p1 = profile_ratings.get_profile(cache, pfd)

        return (np.amax(p0)-np.median(p0))/(np.amax(p1)-np.median(p1))


if __name__=='__main__':
    D = rating.usual_database()
    rating.run(D, 
               [RatioRating(D),
               ])
