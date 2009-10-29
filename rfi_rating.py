import numpy as np
import rating
import MySQLdb

version = 2

fPeriods = np.array([float(p) for p in open('test_cands_periods.txt') if p.strip()])
fRA = np.array([float(ra) for ra in open('test_cands_ra.txt') if ra.strip()])
fDec = np.array([float(decl) for decl in open('test_cands_dec.txt') if decl.strip()])


db = MySQLdb.connect(host="frontend",
			user="palfa",
			passwd="sqlme",
			db="PALFA_v2")

c = db.cursor()



class RFIRating(rating.DatabaseRater):
    def __init__(self,DBconn):
        rating.DatabaseRater.__init__(self,DBconn,version=version,
            name="RFI Rating",
            description="""Determines whether candidates with nearly identical period are RFI based on their sky position.

	Compares each candidate with database of candidates. If the differences in RA and Dec. are both greater than 0.2 degrees, the fractional difference in period is computed. For fractional differences less than 0.001, the value is exponentiated by the number of candidates that fall within that 0.001.

In general, if a candidate gets a rating less than ~1e-4 it's very likely RFI.
 """,
            with_files=False)



    def rate_candidate(self, hdr, candidate, file=None):
        p = candidate["bary_period"]	# get candidate P_bary
	ra = hdr["ra_deg"]		# get candidate R.A.
   	decl = hdr["dec_deg"]		# get candidate Dec.
        pdiff_min = 10     



	c.execute("""SELECT pdm_candidates.period,headers.ra_deg,headers.dec_deg from pdm_candidates,headers where pdm_candidates.header_id=headers.header_id AND abs(pdm_candidates.period-%s)/(pdm_candidates.period+%s) < 0.0002 AND abs(ra_deg-%s) > 0.2 AND abs(dec_deg-%s) > 0.2;""", (p,p,ra,decl))


	results = c.fetchall()
	pdiff_min=3.0/(np.size(results)+1.0)


	return pdiff_min
	

if __name__=='__main__':
    PulsarRating(rating.usual_database()).run()
