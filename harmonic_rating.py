import numpy as np

import rating

version = 1
n = 10
base_f = 60.

class HarmonicRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="Harmonic Rating",
            description="""Evaluate how close the topocentric frequency is to a harmonic or subharmonic of 60 Hz.

Considers all frequencies 60 Hz * a/b where a and b are integers adding up
to less than 10. The fractional difference between the candidate's frequency
and this frequency is computed, and an exponential is taken so that the
result lies between zero and one, reaching 1/2 at a tenth of a percent.
""",
            with_files=False)

    def rate_candidate(self, hdr, candidate, file=None, cache=None):
        f = candidate["frequency"]
        fdiff_min = 1e10
        for a in range(1,9):
            for b in range(1,10-a):
                rf = (base_f * a)/b
                fdiff = 2*abs(f-rf)/(f+rf)
                fdiff_min = min(fdiff,fdiff_min)
        return 2.**(-fdiff_min/1e-3)


if __name__=='__main__':
    D = rating.usual_database()
    rating.run(D, [HarmonicRating(D)])
