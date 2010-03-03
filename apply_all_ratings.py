import sys, datetime

def main():
    import rating
    import harmonic_rating
    import pfd_ratings
    import profile_ratings
    import gaussian_ratings

    if len(sys.argv) > 1:
        where_clause = ' '.join(sys.argv[1:])
	print "Using 'where clause':", where_clause
    else:
	where_clause = None

    D = rating.usual_database()
    rating.run(D,
               [gaussian_ratings.GaussianWidth(D), 
                gaussian_ratings.GaussianHeight(D), 
                profile_ratings.PeakOverRMS(D),
                harmonic_rating.HarmonicRating(D), 
                profile_ratings.DutyCycle(D), 
                pfd_ratings.RatioRating(D), 
               ],
              where_clause=where_clause)

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
    main()
