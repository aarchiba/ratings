import numpy as np
#import math
import rating

version = 1
n = 1833
#psr_period=[]
#psr_name=[]
#psr_ra=[]
#psr_decl=[]
m=99

numerator = np.arange(1,33,dtype=float)
denominator = np.arange(1,5,dtype=float)
outer = np.outer(numerator,1/denominator)
ratios = np.unique(outer[outer!=1])

fPeriods = np.array([float(p) for p in open('knownpulsars_periods.txt') if p.strip()])
fRA = np.array([float(ra) for ra in open('knownpulsars_ra.txt') if ra.strip()])
fDec = np.array([float(decl) for decl in open('knownpulsars_dec.txt') if decl.strip()])
fDM = np.array([float(dm) for dm in open('knownpulsars_dm.txt') if dm.strip()])


class KnownPulsarRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="Known Pulsar Rating",
            description="""Evaluate how close the barycentric period is to a known pulsar, its harmonics (up to 99th), or an integer-ratio-multiple of a known pulsar period.

	Considers all pulsars from the ATNF catalog, as well as known PALFA and DMB pulsars. The known pulsar P, Ra, Dec, and DM are stored in knownpulsars_periods.txt, knownpulsars_ra.txt, knownpulsars_dec.txt, and knownpulsars_dm.txt, resepctively.

1. If the RA -and- Dec separations between the candidate and a pulsar is less than 0.3 degrees, the fractional difference between the candidate's period and pulsar period (or one of its harmonics, up to the 99th) is computed. Otherwise the candidate is given a 0 rating.

2. If this value is less than 0.0002, the fractional difference between the candidate and known pulsar DM is calculated. The rating is then just the inverse of the smallest DM fractional difference.

3. Otherwise, if the fractional difference between the candidate period and an integer-ratio-multiple of a known pulsar period [e.g. (3/16)*P_psr, (5/33)*P_psr] is less than 0.02, the fractional difference in DM is computed. The rating is the inverse of the smallest fractional difference.

Known pulsars should have very high ratings (~>10) and most non-pulsars should be rated with a zero. """,
            with_files=False)


    def rate_candidate(self, hdr, candidate, file=None):
        p = candidate["bary_period"]	# get candidate P_bary
        dm = candidate["dm"]            # get candidate DM
	ra = hdr["ra_deg"]		# R.A.
   	decl = hdr["dec_deg"]		# Dec.
        pdiff_min = 0.0      

	diff_ra=np.abs(fRA-ra)
	diff_dec=np.abs(fDec-decl)



	periods = fPeriods[(diff_ra < 0.3) & (diff_dec < 0.3)]
	dms = fDM[(diff_ra < 0.3) & (diff_dec < 0.3)]




	for b in range(1,m):
	    pdiff = (2.0*np.abs(p*b-periods)/(p*b+periods))

	    if np.any((pdiff < 0.0002)):
		for dispm in dms:
		    	pdiff_dm=1./(2.0*np.abs(((dispm)-dm)/((dispm)+dm)))
			pdiff_min=max(pdiff_dm,pdiff_min)

				
				
	if pdiff_min == 0.0:
	    for rat in ratios:
		pdiff = 2.0*np.abs(((p*rat)-periods)/((p*rat)+periods))
		if np.any((pdiff < 0.02)):
			for dispm in dms:
		        	pdiff_dm=1./(2.0*np.abs(((dispm)-dm)/((dispm)+dm)))

				pdiff_min=max(pdiff_dm,pdiff_min)


	return pdiff_min

if __name__=='__main__':
    PulsarRating(rating.usual_database()).run()
