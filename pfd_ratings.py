import numpy as np

import rating
import profile_rating
import scipy.stats as stats

import copy

class RatioRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=4,
            name="Ratio Rating",
            description="""Compare DM 0 and "best" DM

Computes the ratio of RMS height for the profile dedispersed at
DM 0 divided by that for the profile dedispersed at the best-fit DM.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
        
        p0 = pfd.time_vs_phase().sum(axis=0)
        p1 = profile_rating.get_profile(cache, pfd)

        return np.std(p0)/np.std(p1)


class RatioRatingPeak(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=4,
            name="Ratio Rating Peak",
            description="""Compare DM 0 and "best" DM

Computes the ratio of peak height for the profile dedispersed at
DM 0 divided by that for the profile dedispersed at the best-fit DM.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
        
        p0 = pfd.time_vs_phase().sum(axis=0)

        if "profile" in cache:
            p1 = cache["profile"]
        else:
            if "dedispersed_pfd" in cache:
                pfd = cache["dedispersed_pfd"]
            else:
                oldpfd = pfd
                pfd = copy.deepcopy(pfd)
                pfd.dedisperse(doppler=1)
                pfd_file.profs[0,0,0]+=1
                if np.all(oldpfd.profs == pfd.profs):
                    raise ValueError("copy failed to copy the pfd file")
                pfd_file.profs[0,0,0]-=1
                cache["dedispersed_pfd"] = pfd
            p1 = pfd.time_vs_phase().sum(axis=0)
            p1 -= np.mean(p1)
            cache["profile"] = p1

        return (np.amax(p0)-np.median(p0))/(np.amax(p1)-np.median(p1))


if __name__=='__main__':
    D = rating.usual_database()
    rating.run(D, 
               [RatioRating(D),
               ])
