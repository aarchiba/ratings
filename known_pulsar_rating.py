import numpy as np
#import math
import rating

version = 0
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
            description="""Evaluate how close the barycentric period is to a known pulsar, its harmonics.

	Considers all pulsars from the ATNF catalog, as well as known PALFA and DMB pulsars. If the RA -and- Dec separations between the candidate and known pulsar is less than 10 arcmin. The fractional difference between the candidate's period and this period is computed.  """,
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
#	print periods,dms

	for b in range(1,m):
	    pdiff = (2.0*np.abs(p*b-periods)/(p*b+periods))
#	    print pdiff
	    if np.any((pdiff < 0.0002)):
		        pdiff_min=1./min(2.0*np.abs(((dms)-dm)/((dms)+dm)))
			print pdiff_min,dms			
	if pdiff_min == 0.0:
	    for rat in ratios:
		pdiff = 2.0*np.abs(((p*rat)-periods)/((p*rat)+periods))
		if np.any((pdiff < 0.02)):

		        pdiff_min=1./min(2.0*np.abs(((dms)-dm)/((dms)+dm)))
	return pdiff_min

if __name__=='__main__':
    PulsarRating(rating.usual_database()).run()
