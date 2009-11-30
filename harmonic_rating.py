import numpy as np

import rating

version = 4


class HarmonicRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="Harmonic Rating",
            description="""Evaluate how close the topocentric frequency is to a RFI-prone frequency.

Considers spin frequencies that exhibit a high incidence of RFI (stored in rfi_frequencies.txt). The fractional difference between the candidate's frequency and each RFI frequency is computed and the minimum value is returned. In general, if the rating is less than ~0.001, then the candidate is most likely RFI. 

Should really be called something like --RFI Rating-- instead of --Harmonic Rating--. 
""",
            with_files=False)
	self.fRfi = np.loadtxt("rfi_frequencies.txt", usecols=(0,))


    def rate_candidate(self, hdr, candidate, file=None):
	f = candidate["frequency"]
        fdiffs = 2*np.abs(f-self.fRfi)/(f+self.fRfi)
        return fdiffs.min()


if __name__=='__main__':
    HarmonicRating(rating.usual_database()).run()
