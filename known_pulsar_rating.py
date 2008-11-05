import numpy as np
#import math
import rating

version = 0
n = 1773
psr_period=[]
#psr_name=[]
psr_ra=[]
psr_decl=[]
m=50

numerator = np.arange(1,19,dtype=float)
denominator = np.arange(1,9,dtype=float)
outer = np.outer(numerator,1/denominator)
ratios = np.unique(outer[outer!=1])

fPeriods = np.array([float(p) for p in open('knownpulsars_periods.txt') if p.strip()])
#fNames = open('knownpulsars_names.txt').readlines()
fRA = np.array([float(ra) for ra in open('knownpulsars_ra.txt') if ra.strip()])
fDec = np.array([float(decl) for decl in open('knownpulsars_dec.txt') if decl.strip()])

class KnownPulsarRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="Known Pulsar Rating",
            description="""Evaluate how close the barycentric period is to a known pulsar.

	Considers all pulsars from the ATNF catalog. If the RA -and- Dec separations between the candidate and known pulsar is less than 30 arcmin. The fractional difference
between the candidate's period and this period is computed, and
an exponential is taken so that the result lies between zero and one,
reaching 1/2 at a tenth of a percent.  """,
            with_files=False)

    def rate_candidate(self, hdr, candidate, file=None):
        p = candidate["bary_period"]	# get candidate P_bary
	ra = hdr["ra_deg"]		# R.A.
   	decl = hdr["dec_deg"]		# Dec.
        pdiff_min = 0.0
      
	diff_ra=np.abs(fRA-ra)
	diff_dec=np.abs(fDec-decl)

	periods = fPeriods[(diff_ra < 0.16) & (diff_dec < 0.16)]

	for b in range(1,m):
	    pdiff = (2.0*np.abs(p*b-periods)/(p*b+periods))
	    if np.any((pdiff < 0.005)):
		pdiff_min=1.0
	if pdiff_min != 1.0:
	    for rat in ratios:
		pdiff = 2.0*np.abs(((p*rat)-periods)/((p*rat)+periods))
		if np.any((pdiff < 0.01)):
		    pdiff_min=1.0

	return pdiff_min

if __name__=='__main__':
    PulsarRating(rating.usual_database()).run()
