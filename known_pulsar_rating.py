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
   	dec = hdr["dec_deg"]		# Dec.
        pdiff_min = 0.0
      
	fPeriods = open('knownpulsars_periods.txt').readlines()
#	fNames = open('knownpulsars_names.txt').readlines()
	fRA = open('knownpulsars_ra.txt').readlines()
	fDec = open('knownpulsars_dec.txt').readlines()
        for a in range(0,n):

		psr_ra.append(float(fRA[a]))
		psr_decl.append(float(fDec[a]))
		diff_ra=abs(psr_ra[a]-ra)
		diff_dec=abs(psr_decl[a]-dec)

	

		psr_period.append(float(fPeriods[a]))
#		psr_name.append(fNames[a])
		for b in range(1,m):

	 	        pdiff = (2.*abs(p*b-psr_period[a])/(p*b+psr_period[a]))
	
			if pdiff < 0.005 and diff_ra < 0.16 and diff_dec < 0.16:
#				print '**',b,' harmonic of PSR',psr_name[a],'(P =',psr_period[a],'s) **',

				pdiff_min=1.0

		for c in range(1,19):
			for d in range(1,9):
				rat=float(c)/float(d)
#  						print rat
				pdiff = 2.*abs((p*rat)-psr_period[a])/((p*rat)+psr_period[a])	
				if pdiff < 0.01 and diff_ra < 0.16 and diff_dec < 0.16 and c != d:
#					print '**',c,'/',d,' of PSR',psr_name[a]						
					pdiff_min=1.0

	
#		pdiff_min = min(pdiff,pdiff_min)
#        return 2.**(-pdiff_min/5e-4)
	return pdiff_min



if __name__=='__main__':
    PulsarRating(rating.usual_database()).run()
