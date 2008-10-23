import numpy as np

import rating

version = 1
n = 54


class HarmonicRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="Harmonic Rating",
            description="""Evaluate how close the topocentric frequency is to a RFI-prone frequency.

Considers all frequencies that exhibit a high incidence of RFI. The fractional difference between the candidate's frequency and this frequency is computed.
""",
            with_files=False)

    def rate_candidate(self, hdr, candidate, file=None):
        f = candidate["frequency"]

        fRfi = open('rfi_frequencies.txt').readlines()

        fdiff_min = 1e10

        for a in range(1,n):
#		rf.append(float(fRfi[a]))
                fdiff = 2*abs(f-float(fRfi[a]))/(f+float(fRfi[a]))
                fdiff_min = min(fdiff,fdiff_min)
        return fdiff_min


if __name__=='__main__':
    HarmonicRating(rating.usual_database()).run()
