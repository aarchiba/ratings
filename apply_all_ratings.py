import sys
import datetime
import optparse

def main():
    import rating
    import harmonic_rating
    import pfd_ratings
    import profile_ratings
    import gaussian_ratings

    if options.where is not None:
        print "Using 'where clause':", options.where 

    D = rating.usual_database()
    rating.run(D,
               [gaussian_ratings.GaussianWidth(D), 
                gaussian_ratings.GaussianHeight(D), 
                gaussian_ratings.GaussianPhase(D), 
                harmonic_rating.HarmonicRating(D), 
                profile_ratings.DutyCycle(D), 
                profile_ratings.PrepfoldSigmaRating(D), 
                pfd_ratings.RatioRating(D), 
               ],
              where_clause=options.where,
              scramble=options.scramble,
              limit=options.n)

def print_summary(times):
    print "-"*55
    print "Summary of time spent on each rating:"
    t_tot = datetime.timedelta()
    for name, dt in times:
	print "\t%20s\t %s" % (name, dt)
	t_tot += dt
    print "Total: %s" % t_tot
    print "-"*55
    
	

if __name__=='__main__':
    parser = optparse.OptionParser(usage="%prog [options]", \
                        description="Apply multiple ratings to survey " \
                                    "candidates.", \
                        prog="apply_all_ratings.py")
    parser.add_option("-s", "--scramble", dest="scramble", default=False, \
                        action="store_true", \
                        help="If this flag is set the order in which beams " \
                             "are rated will be randomized. This is useful " \
                             "when running multiple instances of " \
                             "apply_all_ratings.py. (Default: Do not " \
                             "scramble.)")
    parser.add_option("-n", "--only", dest="n", default=-1, type="int", \
                        help="Only rate the first 'n' beams. " \
                             "(Default: -1, rate all beams.)")
    parser.add_option("-w", "--where", dest=None, default="", \
                        help="Where clause to be used when querying " \
                             "the database. (Default: no where clause.)")
    options, args = parser.parse_args()
    main()
