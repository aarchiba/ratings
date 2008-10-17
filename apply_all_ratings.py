import sys, datetime

def main():
    import rating
    import harmonic_rating
    import pfd_ratings
    import profile_ratings

    if len(sys.argv) > 1:
        where_clause = ' '.join(sys.argv[1:])
	print "Using 'where clause':", where_clause
    else:
	where_clause = None

    times = []

    for R in [profile_ratings.GaussianWidth, profile_ratings.GaussianHeight, profile_ratings.PeakOverRMS,harmonic_rating.HarmonicRating, profile_ratings.DutyCycle, pfd_ratings.RatioRating]:
	r = R(rating.usual_database())
	t1 = datetime.datetime.now()
	print "%s: Working on %s" % (t1.strftime("%c"), r.name)
	r.run(where_clause)
	t2 = datetime.datetime.now()
	times.append((r.name, t2-t1))
    print_summary(times)

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
