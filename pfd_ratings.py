import numpy as np

import rating
import prepfold_plus
import scipy.stats as stats

class PrepfoldSigmaRating(rating.DatabaseRater):
    def __init__(self, DBconn):
	rating.DatabaseRater.__init__(self, DBconn, \
	    version = 1, \
	    name = "Prepfold Sigma", \
	    description = "A re-calculation of the sigma value reported on " \
			  "prepfold plots.\n\nCandidates where P(noise) ~ 0 " \
			  "are rated as 99 since a proper sigma value " \
			  "cannot be computed.", \
	    with_files = True, \
	    with_bestprof = True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
	redchi2 = pfd.bestprof.chi_sqr #pfd.calc_redchi2()
	df = pfd.proflen-1 # Degrees of freedom
	
	# pfdsig is negative since we're using survival function
	# instead of cdf.
	pfdsig = -stats.norm.ppf(stats.chi2.sf(redchi2*df, df))
	
	# If pfdsig is infinite set it to a high value, 99.0
	if np.isinf(pfdsig):
            if pfdsig>0:
                pfdsig = 99.0
            else:
                pfdsig = -99.0
	    
	return pfdsig

class PeaksearchRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=2,
            name="Peaksearch Rating",
            description="""Compare peak amplitude to RMS amplitude


""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
        
        pfd.dedisperse(candidate["dm"])
        stds = np.std(pfd.profs,axis=-1)
        s = np.average(stds)/np.sqrt(stds.size)

        p1 = np.average(np.average(pfd.profs,axis=0),axis=0)

        pk = (np.amax(p1)-np.average(p1))/s

        r = -stats.norm.ppf(len(p1)*stats.norm.sf(pk))
        if not np.isfinite(r):
             if r>0: r=99
             else: r=-99
        return r

class RatioRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=2,
            name="Ratio Rating",
            description="""Compare DM 0 and "best" DM

Computes the ratio of peak height for the profile dedispersed at
DM 0 divided by that for the profile dedispersed at the best-fit DM.
""",
            with_files=True)

    def rate_candidate(self, hdr, candidate, pfd, cache=None):
        
        p0 = np.sum(np.sum(pfd.profs,axis=0),axis=0)
        pfd.dedisperse(candidate["dm"])
        p1 = np.sum(np.sum(pfd.profs,axis=0),axis=0)

        return (np.amax(p0)-np.mean(p0))/(np.amax(p1)-np.mean(p1))


if __name__=='__main__':
    RatioRating(rating.usual_database()).run()
    PrepfoldSigmaRating(rating.usual_database()).run()
    PeaksearchRating(rating.usual_database()).run()
