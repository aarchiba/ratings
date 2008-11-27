import numpy as np

import rating

version = 2
n = 132

fRfi = np.array([float(r) for r in open('rfi_frequencies.txt') if r.strip()])

class HarmonicRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="Harmonic Rating",
            description="""Evaluate how close the topocentric frequency is to a RFI-prone frequency.

Considers spin frequencies that exhibit a high incidence of RFI (stored in rfi_frequencies.txt). The fractional difference between the candidate's frequency and each RFI frequency is computed and the minimum value is returned. In general, if the rating is less than 0.001, then the candidate is most likely RFI. 

Should really be called --RFI Rating-- instead of --Harmonic Rating--. 
""",
            with_files=False)

#	fRfi.sort()
#	print fRfi

    def rate_candidate(self, hdr, candidate, file=None):
        f = candidate["frequency"]

#        fRfi = open('rfi_frequencies.txt').readlines()



        fdiff_min = 1e10

        for a in range(1,n):
                fdiff = 2*abs(f-float(fRfi[a]))/(f+float(fRfi[a]))
                fdiff_min = min(fdiff,fdiff_min)

#	rf.sort()
#	print rf	

	
        return fdiff_min




if __name__=='__main__':
    HarmonicRating(rating.usual_database()).run()
